from __future__ import annotations

import json
import math
import sqlite3
from pathlib import Path
from typing import Any

from .bank import catalog_ready, jsonl_path, load_policy, read_lock, resolve_design_v2_root
from .dna import extract_query, score_dna, slop_penalty, tokenize
from .schema import load_jsonl


def _weights(policy: dict[str, Any]) -> dict[str, float]:
    raw = (policy.get("search") or {}).get("weights") or {}
    return {str(k): float(v) for k, v in raw.items()}


def lexical_score(item: dict[str, Any], query: str, policy: dict[str, Any]) -> tuple[float, list[str]]:
    weights = _weights(policy)
    q_tokens = set(tokenize(query))
    if not q_tokens:
        return 0.0, []
    fields = {
        "name": item.get("name") or "",
        "id": item.get("id") or "",
        "description": item.get("description") or "",
        "category": " ".join(item.get("categories") or []),
        "tags": " ".join(item.get("tags") or []),
        "summary": item.get("search_text") or "",
    }
    score = 0.0
    matched: list[str] = []
    for field, blob in fields.items():
        overlap = q_tokens & set(tokenize(str(blob)))
        if not overlap:
            continue
        score += float(weights.get(field) or 1.0) * len(overlap) / math.sqrt(len(q_tokens))
        matched.append(field)
    return score, matched


VISUAL_KINDS = frozenset(
    {
        "visual",
        "section",
        "page",
        "template",
        "block",
        "component",
        "primitive",
        "theme",
        "motion",
        "effect",
        "background",
        "pattern",
    }
)


def eligible(
    item: dict[str, Any],
    kind: str | None,
    kinds: frozenset[str] | set[str] | None = None,
) -> tuple[bool, str]:
    if item.get("alias_of") or item.get("duplicate_of"):
        return False, "alias_or_duplicate"
    if item.get("search_policy") == "never":
        return False, "search_policy"
    license_obj = item.get("license") or {}
    if license_obj.get("redistribution") == "blocked" or license_obj.get("status") == "conflicting":
        return False, "blocked_license"
    if item.get("execution_class") == "quarantined":
        return False, "quarantined"
    if kinds:
        if item.get("kind") not in kinds:
            return False, "kind"
    elif kind and item.get("kind") != kind:
        return False, "kind"
    return True, "ok"


def diversity_penalty(selected: list[dict[str, Any]], candidate: dict[str, Any], penalty: float) -> float:
    cats = set(candidate.get("categories") or [])
    if not cats:
        return 0.0
    hits = 0
    for item in selected:
        if cats & set(item.get("categories") or []):
            hits += 1
    return hits * penalty


def _fts_query(query: str) -> str:
    tokens = tokenize(query)
    return " OR ".join(tokens)


def _fts_ids(sqlite_path: Path, query: str, limit: int) -> list[str] | None:
    match = _fts_query(query)
    if not match:
        return []
    try:
        conn = sqlite3.connect(f"file:{sqlite_path}?mode=ro", uri=True)
    except sqlite3.Error:
        return None
    try:
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='items_fts'")
        if cur.fetchone() is None:
            return None
        rows = conn.execute(
            "SELECT id FROM items_fts WHERE items_fts MATCH ? LIMIT ?",
            (match, limit),
        ).fetchall()
        return [str(row[0]) for row in rows]
    except sqlite3.Error:
        return None
    finally:
        conn.close()


def load_catalog(root: Path) -> tuple[list[dict[str, Any]], dict[str, Any] | None, str]:
    if not catalog_ready(root):
        return [], None, "EMPTY"
    lock = read_lock(root)
    path = jsonl_path(root, lock)
    if not lock or not path:
        return [], lock, "DEGRADED"
    try:
        items = load_jsonl(path)
    except (OSError, ValueError, json.JSONDecodeError):
        return [], lock, "DEGRADED"
    return items, lock, "ok"


def search(
    query: str,
    *,
    root: Path | None = None,
    kind: str | None = None,
    kinds: frozenset[str] | set[str] | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    policy = load_policy()
    bank = root if root is not None else resolve_design_v2_root()
    search_cfg = policy.get("search") or {}
    candidate_limit = int(search_cfg.get("candidate_limit") or 50)
    result_limit = int(limit if limit is not None else search_cfg.get("result_limit") or 5)
    penalty = float(search_cfg.get("diversity_penalty") or 4.0)
    min_score = float(search_cfg.get("min_score") or 0.01)
    extracted = extract_query(query)

    items, lock, bank_status = load_catalog(bank)
    if bank_status != "ok":
        return {
            "query": query,
            "kind": kind,
            "results": [],
            "bank_status": bank_status,
            "retrieval": "none",
            "packages_loaded_during_search": 0,
            "dna": extracted,
        }

    fts = lock.get("fts") if isinstance(lock, dict) else None
    retrieval = "jsonl"
    candidates = items
    if isinstance(fts, dict) and fts.get("status") == "available" and fts.get("sqlite_filename"):
        sqlite_path = bank / "catalog" / str(fts["sqlite_filename"])
        ids = _fts_ids(sqlite_path, query, candidate_limit)
        if ids is not None:
            by_id = {item["id"]: item for item in items}
            ordered = [by_id[i] for i in ids if i in by_id]
            if ordered:
                candidates = ordered
                retrieval = "fts5"

    scored: list[tuple[float, dict[str, Any], list[str]]] = []
    for item in candidates:
        ok, _reason = eligible(item, kind, kinds=kinds)
        if not ok:
            continue
        points, matched = lexical_score(item, query, policy)
        points += score_dna(item, extracted, policy)
        points -= slop_penalty(item, extracted, policy)
        if points <= 0 or points < min_score:
            continue
        scored.append((points, item, matched))
    if retrieval == "jsonl" and len(scored) > candidate_limit:
        scored.sort(key=lambda row: (-row[0], row[1]["id"]))
        scored = scored[:candidate_limit]
    else:
        scored.sort(key=lambda row: (-row[0], row[1]["id"]))

    picked: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    pending = list(scored)
    while pending and len(results) < result_limit:
        best_index = 0
        best_adj: float | None = None
        for index, (points, item, matched) in enumerate(pending):
            adj = points - diversity_penalty(picked, item, penalty)
            if best_adj is None or adj > best_adj or (adj == best_adj and item["id"] < pending[best_index][1]["id"]):
                best_adj = adj
                best_index = index
        if best_adj is None or best_adj <= 0:
            break
        points, item, matched = pending.pop(best_index)
        adj = points - diversity_penalty(picked, item, penalty)
        picked.append(item)
        results.append(
            {
                "id": item["id"],
                "kind": item.get("kind"),
                "role": item.get("role"),
                "name": item.get("name"),
                "description": item.get("description"),
                "score": adj,
                "matched_fields": matched,
                "license": item.get("license"),
                "dna": item.get("dna") or {},
                "untrusted_text": True,
            }
        )
    return {
        "query": query,
        "kind": kind,
        "results": results,
        "bank_status": "ok",
        "retrieval": retrieval,
        "packages_loaded_during_search": 0,
        "dna": {k: v for k, v in extracted.items() if k != "tokens"},
        "fts": fts,
    }


def shortlist(
    query: str,
    *,
    root: Path | None = None,
    intent: str | None = None,
    mode: str | None = None,
    structure_only: bool = False,
) -> dict[str, Any]:
    bank = root if root is not None else resolve_design_v2_root()
    items, lock, bank_status = load_catalog(bank)
    payload: dict[str, Any] = {
        "status": "ok" if bank_status == "ok" else bank_status,
        "query": query,
        "intent": intent,
        "mode": mode,
        "systems": [],
        "structures": [],
        "visuals": [],
        "limits": {
            "systems": 0 if structure_only else 5,
            "structures": 3,
            "visuals": 0 if structure_only else 5,
        },
        "packages_loaded_during_search": 0,
        "untrusted_text": True,
        "offline": True,
        "bank_status": bank_status,
        "catalog_generation": (lock or {}).get("generation_id") if isinstance(lock, dict) else None,
    }
    if bank_status != "ok" or not items:
        return payload
    if not structure_only:
        payload["systems"] = search(query, root=bank, kind="system", limit=5)["results"]
        payload["visuals"] = search(query, root=bank, kinds=VISUAL_KINDS, limit=5)["results"]
    payload["structures"] = search(query, root=bank, kind="structure", limit=3)["results"]
    return payload

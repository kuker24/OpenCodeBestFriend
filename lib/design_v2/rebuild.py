from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import FTS_SCHEMA_VERSION, SKIP_FTS_VAR
from .bank import DesignV2Error, assert_under_v2, ensure_layout, env_get, load_policy, read_lock
from .schema import check_item, dump_line, load_jsonl


class RebuildError(DesignV2Error):
    code = "REBUILD_FAILED"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def generation_id_for(jsonl_bytes: bytes, input_hashes: dict[str, str]) -> str:
    h = hashlib.sha256()
    h.update(jsonl_bytes)
    for name in sorted(input_hashes):
        h.update(name.encode("utf-8"))
        h.update(str(input_hashes[name]).encode("ascii"))
    return h.hexdigest()[:16]


def _inbox_items(root: Path, policy: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, str], list[str]]:
    inbox = root / "inbox"
    items: list[dict[str, Any]] = []
    hashes: dict[str, str] = {}
    errors: list[str] = []
    if not inbox.is_dir():
        return items, hashes, errors
    for path in sorted(inbox.glob("*.json")):
        raw = path.read_bytes()
        hashes[path.name] = _sha256_bytes(raw)
        try:
            item = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            errors.append(f"{path.name}:json")
            continue
        if not isinstance(item, dict):
            errors.append(f"{path.name}:item")
            continue
        problems = check_item(item, policy)
        if problems:
            errors.append(f"{path.name}:{','.join(problems[:8])}")
            continue
        items.append(item)
    return items, hashes, errors


def _write_sqlite(path: Path, items: list[dict[str, Any]]) -> str:
    conn = sqlite3.connect(path)
    try:
        conn.execute("CREATE TABLE items (id TEXT PRIMARY KEY, kind TEXT, json TEXT NOT NULL)")
        conn.executemany(
            "INSERT INTO items(id, kind, json) VALUES (?, ?, ?)",
            [(item["id"], item.get("kind") or "", dump_line(item)) for item in items],
        )
        conn.execute(
            "CREATE VIRTUAL TABLE items_fts USING fts5("
            "id UNINDEXED, name, description, search_text, kind, tags, categories, intent, modes, frameworks, "
            "product_fit, anti_slop, dna)"
        )
        conn.executemany(
            "INSERT INTO items_fts("
            "id, name, description, search_text, kind, tags, categories, intent, modes, frameworks, "
            "product_fit, anti_slop, dna"
            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    item["id"],
                    item.get("name") or "",
                    item.get("description") or "",
                    item.get("search_text") or "",
                    item.get("kind") or "",
                    " ".join(item.get("tags") or []),
                    " ".join(item.get("categories") or []),
                    " ".join(item.get("intent") or []),
                    " ".join(item.get("modes") or []),
                    " ".join(item.get("frameworks") or []),
                    " ".join(item.get("product_fit") or []),
                    " ".join(item.get("anti_slop") or []),
                    " ".join(
                        str(value)
                        for raw in (item.get("dna") or {}).values()
                        for value in (raw if isinstance(raw, list) else [raw])
                        if value
                    ),
                )
                for item in items
            ],
        )
        conn.commit()
    finally:
        conn.close()
    return "available"


def _fts_status_for_error(exc: BaseException) -> str:
    text = str(exc).lower()
    if "fts5" in text or "no such module" in text:
        return "unavailable"
    return "failed"


def _build_fts(path: Path, items: list[dict[str, Any]], sqlite_name: str) -> dict[str, Any]:
    try:
        _write_sqlite(path, items)
        return {
            "status": "available",
            "sqlite_filename": sqlite_name,
            "sqlite_sha256": _sha256_bytes(path.read_bytes()),
            "schema_version": FTS_SCHEMA_VERSION,
        }
    except sqlite3.OperationalError as exc:
        status = _fts_status_for_error(exc)
    except Exception:
        status = "failed"
    if path.exists():
        path.unlink()
    return {
        "status": status,
        "sqlite_filename": None,
        "sqlite_sha256": None,
        "schema_version": FTS_SCHEMA_VERSION,
    }


def _fts_is_current(root: Path, fts: dict[str, Any]) -> bool:
    if fts.get("status") != "available" or fts.get("schema_version") != FTS_SCHEMA_VERSION:
        return False
    name = str(fts.get("sqlite_filename") or "")
    expected = str(fts.get("sqlite_sha256") or "")
    path = root / "catalog" / name
    return bool(name and expected and path.is_file() and _sha256_bytes(path.read_bytes()) == expected)


def _refresh_fts(
    root: Path,
    dirs: dict[str, Path],
    existing: dict[str, Any],
    items: list[dict[str, Any]],
) -> dict[str, Any]:
    generation_id = str(existing["generation_id"])
    sqlite_name = f"catalog-{generation_id}.sqlite3"
    incoming = Path(tempfile.mkdtemp(prefix="v2-fts-", dir=str(dirs["tmp"])))
    assert_under_v2(root, incoming)
    try:
        incoming_sqlite = incoming / sqlite_name
        fts = _build_fts(incoming_sqlite, items, sqlite_name)
        if fts["status"] == "available":
            os.replace(incoming_sqlite, dirs["catalog"] / sqlite_name)
        elif _fts_is_current(root, existing.get("fts") or {}):
            return existing["fts"]
        lock_doc = dict(existing)
        lock_doc["fts"] = fts
        _atomic_write_json(dirs["catalog"] / "catalog.lock.json", lock_doc)
        return fts
    finally:
        shutil.rmtree(incoming, ignore_errors=True)


def _gc(catalog: Path, current: str, keep: int) -> None:
    live = {f"catalog-{current}.jsonl", f"catalog-{current}.sqlite3", "catalog.lock.json"}
    lock = catalog / "catalog.lock.json"
    if lock.is_file():
        try:
            doc = json.loads(lock.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            doc = {}
        live.add(str(doc.get("jsonl_filename") or ""))
        raw_fts = doc.get("fts")
        fts_doc: dict[str, Any] = raw_fts if isinstance(raw_fts, dict) else {}
        live.add(str(fts_doc.get("sqlite_filename") or ""))
    gens: list[str] = []
    for path in catalog.glob("catalog-*.jsonl"):
        gens.append(path.name[len("catalog-") : -len(".jsonl")])
    gens = sorted(set(gens))
    if current in gens:
        gens.remove(current)
        gens.append(current)
    drop = gens[:-keep] if keep > 0 else gens
    for gid in drop:
        for name in (f"catalog-{gid}.jsonl", f"catalog-{gid}.sqlite3"):
            target = catalog / name
            if target.is_file() and target.name not in live:
                target.unlink()


def rebuild(root: Path, *, now: datetime | None = None) -> dict[str, Any]:
    policy = load_policy()
    dirs = ensure_layout(root)
    items, input_hashes, errors = _inbox_items(root, policy)
    if errors:
        payload = {"error": "schema_invalid", "items": errors[:32]}
        _atomic_write_json(dirs["reports"] / "rebuild-failed.json", payload)
        raise RebuildError("schema_invalid:" + ";".join(errors[:8]))
    items.sort(key=lambda row: row["id"])
    jsonl = "".join(dump_line(item) + "\n" for item in items)
    jsonl_bytes = jsonl.encode("utf-8")
    generation_id = generation_id_for(jsonl_bytes, input_hashes)
    clock = now or datetime.now(timezone.utc)

    existing = read_lock(root)
    jsonl_name = f"catalog-{generation_id}.jsonl"
    existing_jsonl = root / "catalog" / jsonl_name
    same_generation = (
        existing
        and existing.get("generation_id") == generation_id
        and existing.get("jsonl_filename") == jsonl_name
        and existing_jsonl.is_file()
        and str(existing.get("jsonl_sha256") or "") == _sha256_bytes(existing_jsonl.read_bytes())
    )
    skip_fts = env_get(SKIP_FTS_VAR) == "1"
    if same_generation:
        assert existing is not None
        raw_fts = existing.get("fts")
        existing_fts: dict[str, Any] = raw_fts if isinstance(raw_fts, dict) else {}
        if skip_fts or _fts_is_current(root, existing_fts):
            fts = existing_fts
            fts_rebuilt = False
        else:
            fts = _refresh_fts(root, dirs, existing, items)
            fts_rebuilt = True
        return {
            "status": "ok",
            "generation_id": generation_id,
            "reused": True,
            "item_count": len(items),
            "fts": fts,
            "fts_rebuilt": fts_rebuilt,
        }

    incoming = Path(tempfile.mkdtemp(prefix="v2-incoming-", dir=str(dirs["tmp"])))
    assert_under_v2(root, incoming)
    fts: dict[str, Any] = {
        "status": "skipped",
        "sqlite_filename": None,
        "sqlite_sha256": None,
        "schema_version": FTS_SCHEMA_VERSION,
    }
    try:
        incoming_jsonl = incoming / jsonl_name
        incoming_jsonl.write_bytes(jsonl_bytes)
        jsonl_sha = _sha256_bytes(incoming_jsonl.read_bytes())
        sqlite_name = f"catalog-{generation_id}.sqlite3"
        if skip_fts:
            fts["status"] = "skipped"
        else:
            incoming_sqlite = incoming / sqlite_name
            fts = _build_fts(incoming_sqlite, items, sqlite_name)
        final_jsonl = dirs["catalog"] / jsonl_name
        os.replace(incoming_jsonl, final_jsonl)
        if fts.get("sqlite_filename"):
            os.replace(incoming / sqlite_name, dirs["catalog"] / sqlite_name)
        lock_doc = {
            "generation_id": generation_id,
            "schema_version": 2,
            "jsonl_filename": jsonl_name,
            "jsonl_sha256": jsonl_sha,
            "fts": fts,
            "input_hashes": input_hashes,
            "created_at": clock.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "item_count": len(items),
        }
        _atomic_write_json(dirs["catalog"] / "catalog.lock.json", lock_doc)
    except RebuildError:
        raise
    except Exception as exc:
        _atomic_write_json(
            dirs["reports"] / "rebuild-failed.json",
            {"error": "rebuild_failed", "generation_id": generation_id, "detail": type(exc).__name__},
        )
        raise RebuildError("rebuild_failed") from exc
    finally:
        shutil.rmtree(incoming, ignore_errors=True)

    _gc(dirs["catalog"], generation_id, int(policy.get("keep_generations") or 2))
    return {
        "status": "ok",
        "generation_id": generation_id,
        "reused": False,
        "item_count": len(items),
        "fts": fts,
    }

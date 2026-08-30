from __future__ import annotations

import json
import sys
from argparse import Namespace
from pathlib import Path
from typing import Any

from .bank import (
    DesignV2Error,
    bank_present,
    catalog_ready,
    list_sources,
    load_policy,
    read_lock,
    resolve_design_v2_root,
)
from .dedupe import dedupe
from .import_stage import import_stage
from .ingest import ingest
from .inspect import inspect_item
from .rebuild import RebuildError, rebuild
from .schema import check_lock
from .search import search, shortlist


def _emit(payload: object) -> int:
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))
    return 0


def _line(status: str, label: str, evidence: str = "") -> None:
    print(f"{status:<22} {label:<28} {evidence}")


def cmd_status(root: Path | None = None) -> int:
    bank = root if root is not None else resolve_design_v2_root()
    _line("INFO", "root", str(bank))
    _line("INFO", "offline", "yes")
    if not bank_present(bank):
        _line("EMPTY", "DesignV2", "absent")
        return 0
    if not catalog_ready(bank):
        _line("DEGRADED", "DesignV2", "no-catalog")
        return 0
    lock = read_lock(bank)
    if not lock:
        _line("DEGRADED", "DesignV2", "lock-unreadable")
        return 0
    _line("PASS", "catalog", str(lock.get("generation_id") or ""))
    _line("INFO", "items", str(lock.get("item_count", "")))
    raw_fts = lock.get("fts")
    fts: dict[str, Any] = raw_fts if isinstance(raw_fts, dict) else {}
    status = str(fts.get("status") or "unavailable")
    label = "DEGRADED_FTS" if status != "available" else "PASS"
    _line(label, "fts", status)
    return 0


def cmd_search(query: str, *, kind: str | None = None, limit: int | None = None, root: Path | None = None) -> int:
    payload = search(query, root=root, kind=kind, limit=limit)
    return _emit(payload)


def cmd_inspect(item_id: str, *, root: Path | None = None) -> int:
    payload = inspect_item(item_id, root=root)
    rc = 0 if "error" not in payload else 1
    _emit(payload)
    return rc


def cmd_rebuild(root: Path | None = None) -> int:
    bank = root if root is not None else resolve_design_v2_root()
    try:
        payload = rebuild(bank)
    except RebuildError as exc:
        print(f"FAIL {exc.code} {exc}", file=sys.stderr)
        return 1
    return _emit(payload)


def doctor_rows(root: Path | None = None) -> list[tuple[str, str, str]]:
    bank = root if root is not None else resolve_design_v2_root()
    rows: list[tuple[str, str, str]] = [("INFO", "root", str(bank))]
    policy = load_policy()
    if policy.get("schema_version") != 2:
        rows.append(("FAIL", "policy", "schema"))
        return rows
    rows.append(("PASS", "policy", "v2"))
    if not bank_present(bank):
        rows.append(("EMPTY", "bank", "absent"))
        return rows
    if not catalog_ready(bank):
        rows.append(("DEGRADED", "bank", "no-catalog"))
        return rows
    lock = read_lock(bank)
    if not lock:
        rows.append(("FAIL", "lock", "unreadable"))
        return rows
    errors = check_lock(lock)
    if errors:
        rows.append(("FAIL", "lock", ",".join(errors[:6])))
        return rows
    rows.append(("PASS", "lock", str(lock.get("generation_id") or "")))
    jsonl_name = str(lock.get("jsonl_filename") or "")
    jsonl = bank / "catalog" / jsonl_name
    if not jsonl.is_file():
        rows.append(("FAIL", "jsonl", "missing"))
        return rows
    rows.append(("PASS", "jsonl", jsonl_name))
    raw_fts = lock.get("fts")
    fts: dict[str, Any] = raw_fts if isinstance(raw_fts, dict) else {}
    fts_status = str(fts.get("status") or "unavailable")
    if fts_status == "available":
        sqlite_name = fts.get("sqlite_filename")
        sqlite_path = bank / "catalog" / str(sqlite_name)
        if sqlite_name and sqlite_path.is_file():
            rows.append(("PASS", "fts", "available"))
        else:
            rows.append(("DEGRADED_FTS", "fts", "sqlite-missing"))
    else:
        rows.append(("DEGRADED_FTS", "fts", fts_status))
    return rows


def product_doctor_rows(root: Path | None = None) -> list[tuple[str, str, str]]:
    mapped: list[tuple[str, str, str]] = []
    labels = {
        "root": "Design V2 root",
        "policy": "Design V2 policy",
        "bank": "Design V2",
        "lock": "Design V2 lock",
        "jsonl": "Design V2 jsonl",
        "fts": "Design V2 fts",
    }
    for status, label, evidence in doctor_rows(root):
        mapped.append((status, labels.get(label, f"Design V2 {label}"), evidence))
    return mapped


def cmd_doctor(root: Path | None = None) -> int:
    rows = doctor_rows(root)
    rc = 0
    for status, label, evidence in rows:
        _line(status, label, evidence)
        if status == "FAIL":
            rc = 1
    return rc


def cmd_import(path: Path, *, provider: str = "manual", root: Path | None = None) -> int:
    bank = root if root is not None else resolve_design_v2_root()
    return _emit(import_stage(path, bank, provider=provider))


def cmd_sources(root: Path | None = None) -> int:
    return _emit(list_sources(root))


def cmd_shortlist(
    query: str,
    *,
    root: Path | None = None,
    intent: str | None = None,
    mode: str | None = None,
    structure_only: bool = False,
) -> int:
    return _emit(
        shortlist(query, root=root, intent=intent, mode=mode, structure_only=structure_only)
    )


def dispatch(args: Namespace) -> int:
    action = getattr(args, "design_action", None) or getattr(args, "action", None)
    root = Path(args.bank).expanduser() if getattr(args, "bank", None) else None
    try:
        if action == "status":
            return cmd_status(root)
        if action == "search":
            query = getattr(args, "query", None) or getattr(args, "target", None)
            if not query:
                print("FAIL missing query", file=sys.stderr)
                return 2
            return cmd_search(query, kind=getattr(args, "kind", None), limit=getattr(args, "limit", None), root=root)
        if action == "inspect":
            item_id = getattr(args, "target", None)
            if not item_id:
                print("FAIL missing id", file=sys.stderr)
                return 2
            return cmd_inspect(item_id, root=root)
        if action == "rebuild":
            return cmd_rebuild(root)
        if action == "doctor":
            return cmd_doctor(root)
        if action == "ingest":
            path = Path(args.target).expanduser() if getattr(args, "target", None) else None
            payload = ingest(root, provider=getattr(args, "provider", None), path=path)
            return _emit(payload)
        if action == "import":
            target = getattr(args, "target", None)
            if not target:
                print("FAIL missing path", file=sys.stderr)
                return 2
            return cmd_import(
                Path(target).expanduser(),
                provider=getattr(args, "provider", None) or "manual",
                root=root,
            )
        if action == "sources":
            return cmd_sources(root)
        if action == "shortlist":
            query = getattr(args, "query", None) or getattr(args, "target", None)
            if not query:
                print("FAIL missing query", file=sys.stderr)
                return 2
            return cmd_shortlist(
                query,
                root=root,
                intent=getattr(args, "intent", None),
                mode=getattr(args, "mode", None),
                structure_only=bool(getattr(args, "structure_only", False)),
            )
        if action == "dedupe":
            return _emit(dedupe(root))
    except DesignV2Error as exc:
        print(f"FAIL {exc.code} {exc}", file=sys.stderr)
        return 1
    print("FAIL unknown design action", file=sys.stderr)
    return 2

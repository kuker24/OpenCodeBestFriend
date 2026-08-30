from __future__ import annotations

import json
import re
import sys
from argparse import ArgumentParser, Namespace
from collections import Counter
from pathlib import Path
from typing import Any

from ..common import sha256_file
from . import FTS_SCHEMA_VERSION
from .bank import (
    SOURCE_PROVIDERS,
    DesignV2Error,
    PathEscape,
    assert_under_v2,
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
from .search import load_catalog, search, shortlist

REMOTE_INPUT_RE = re.compile(r"^(?:[A-Za-z][A-Za-z0-9+.-]*:|//)")
STAGED_PROVIDERS = ("aura", "21st", "open-design", "github-oss", "manual")
INGEST_PROVIDERS = SOURCE_PROVIDERS + ("bank-pointer",)


def add_design_cli(parser: ArgumentParser, *, read_only: bool = False) -> None:
    parser.description = "Offline DesignV2 lifecycle and retrieval"
    parser.epilog = (
        "Lifecycle: import LOCAL_PATH -> sources -> ingest --source-id ID -> dedupe -> rebuild -> "
        "doctor -> search/shortlist -> inspect. Commands never fetch URLs."
    )
    actions = parser.add_subparsers(dest="design_action", required=True, title="actions")

    def common(action: str, help_text: str) -> ArgumentParser:
        child = actions.add_parser(action, help=help_text, description=help_text)
        child.add_argument("--bank", help="DesignV2 root (default: OPENCODE_DESIGN_V2 or ~/DesignV2)")
        child.add_argument("--json", action="store_true", help="emit machine-readable JSON where default is human output")
        return child

    status = common("status", "show offline bank and catalog status")
    del status

    search_parser = common("search", "search committed metadata without opening asset folders")
    search_parser.add_argument("target", nargs="?", metavar="QUERY")
    search_parser.add_argument("--query")
    search_parser.add_argument("--kind")
    search_parser.add_argument("--limit", type=int, help="result count, 1-50")
    search_parser.add_argument("--intent")
    search_parser.add_argument("--mode")
    search_parser.add_argument("--framework", action="append")

    inspect_parser = common("inspect", "inspect one selected catalog item lazily")
    inspect_parser.add_argument("target", nargs="?", metavar="ID")

    doctor = common("doctor", "verify catalog integrity and report bounded bank health")
    del doctor
    sources = common("sources", "list staged local sources and stable source IDs")
    del sources

    shortlist_parser = common("shortlist", "return bounded offline reasoning cards")
    shortlist_parser.add_argument("target", nargs="?", metavar="QUERY")
    shortlist_parser.add_argument("--query")
    shortlist_parser.add_argument("--limit", type=int, help="per-lane result count, 1-5")
    shortlist_parser.add_argument("--intent")
    shortlist_parser.add_argument("--mode")
    shortlist_parser.add_argument("--framework", action="append")
    shortlist_parser.add_argument("--structure-only", action="store_true")

    if read_only:
        return

    rebuild_parser = common("rebuild", "atomically rebuild canonical JSONL and optional FTS5")
    del rebuild_parser
    dedupe_parser = common("dedupe", "mark aliases and duplicates without deleting assets")
    del dedupe_parser

    import_parser = common("import", "security-stage a user-supplied local file, folder, or ZIP")
    import_parser.add_argument("target", nargs="?", metavar="LOCAL_PATH")
    import_parser.add_argument("--provider", choices=STAGED_PROVIDERS, default="manual")

    ingest_parser = common("ingest", "normalize a staged source ID or a local path")
    ingest_parser.add_argument("target", nargs="?", metavar="LOCAL_PATH")
    ingest_parser.add_argument("--provider", choices=INGEST_PROVIDERS)
    ingest_parser.add_argument("--source-id", help="16-character ID returned by design import/sources")


def _local_input(raw: str) -> Path:
    if REMOTE_INPUT_RE.match(raw.strip()):
        raise DesignV2Error(
            "local path required; obtain or export the files first",
            code="REMOTE_URL_REJECTED",
        )
    return Path(raw).expanduser()


def _fail(action: str, code: str, message: str, *, json_output: bool, exit_code: int = 1) -> int:
    if json_output:
        print(
            json.dumps(
                {"schema_version": 1, "action": action, "status": "error", "error": {"code": code, "message": message}},
                sort_keys=True,
            ),
            file=sys.stderr,
        )
    else:
        print(f"FAIL {code} {message}", file=sys.stderr)
    return exit_code


def _emit(payload: object) -> int:
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))
    return 0


def _line(status: str, label: str, evidence: str = "") -> None:
    print(f"{status:<22} {label:<28} {evidence}")


def status_rows(root: Path | None = None) -> list[tuple[str, str, str]]:
    bank = root if root is not None else resolve_design_v2_root()
    rows: list[tuple[str, str, str]] = [("INFO", "root", str(bank)), ("INFO", "offline", "yes")]
    if not bank_present(bank):
        rows.append(("EMPTY", "DesignV2", "absent"))
        return rows
    if not catalog_ready(bank):
        rows.append(("DEGRADED", "DesignV2", "no-catalog"))
        return rows
    lock = read_lock(bank)
    if not lock:
        rows.append(("DEGRADED", "DesignV2", "lock-unreadable"))
        return rows
    rows.append(("PASS", "catalog", str(lock.get("generation_id") or "")))
    rows.append(("INFO", "items", str(lock.get("item_count", ""))))
    raw_fts = lock.get("fts")
    fts: dict[str, Any] = raw_fts if isinstance(raw_fts, dict) else {}
    status = str(fts.get("status") or "unavailable")
    current = status == "available" and fts.get("schema_version") == FTS_SCHEMA_VERSION
    label = "PASS" if current else "DEGRADED_FTS"
    evidence = status if current or status != "available" else "schema-old"
    rows.append((label, "fts", evidence))
    return rows


def cmd_status(root: Path | None = None, *, json_output: bool = False) -> int:
    rows = status_rows(root)
    if json_output:
        return _emit(
            {
                "schema_version": 1,
                "action": "status",
                "status": "ok",
                "offline": True,
                "checks": [
                    {"status": status, "label": label, "evidence": evidence}
                    for status, label, evidence in rows
                ],
            }
        )
    for status, label, evidence in rows:
        _line(status, label, evidence)
    return 0


def cmd_search(
    query: str,
    *,
    kind: str | None = None,
    limit: int | None = None,
    root: Path | None = None,
    intent: str | None = None,
    mode: str | None = None,
    frameworks: list[str] | None = None,
) -> int:
    payload = search(
        query,
        root=root,
        kind=kind,
        limit=limit,
        intent=intent,
        mode=mode,
        frameworks=frameworks,
    )
    return _emit(payload)


def cmd_inspect(item_id: str, *, root: Path | None = None) -> int:
    payload = inspect_item(item_id, root=root)
    rc = 0 if "error" not in payload else 1
    _emit(payload)
    return rc


def cmd_rebuild(root: Path | None = None, *, json_output: bool = False) -> int:
    bank = root if root is not None else resolve_design_v2_root()
    try:
        payload = rebuild(bank)
    except RebuildError as exc:
        return _fail("rebuild", exc.code, str(exc), json_output=json_output)
    return _emit(payload)


def _bounded_counts(values: list[str], *, limit: int = 12) -> dict[str, int]:
    counts = Counter(value or "unknown" for value in values)
    ordered = sorted(counts.items(), key=lambda row: (-row[1], row[0]))
    result = dict(ordered[:limit])
    omitted = sum(count for _name, count in ordered[limit:])
    if omitted:
        result["__other__"] = omitted
    return result


def _pointer_is_broken(bank: Path, provider: str) -> bool:
    path = bank / "sources" / provider / "pointer.json"
    if not path.is_file():
        return False
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return True
    if not isinstance(payload, dict):
        return True
    root = payload.get("root")
    catalog = payload.get("catalog")
    if not isinstance(root, str) or not isinstance(catalog, str):
        return True
    relative = Path(catalog)
    if relative.is_absolute() or ".." in relative.parts:
        return True
    return not (Path(root).expanduser() / relative).is_file()


def bank_health(root: Path | None = None) -> dict[str, Any]:
    bank = root if root is not None else resolve_design_v2_root()
    items, lock, catalog_status = load_catalog(bank)
    health: dict[str, Any] = {
        "root": str(bank),
        "offline": True,
        "catalog_status": catalog_status,
        "catalog_generation": (lock or {}).get("generation_id") if isinstance(lock, dict) else None,
        "total_assets": 0,
    }
    if catalog_status != "ok":
        return health

    missing_local: list[str] = []
    weak_metadata: list[str] = []
    no_product_fit: list[str] = []
    no_frameworks: list[str] = []
    dna_dimensions: list[str] = []
    providers: list[str] = []
    kinds: list[str] = []
    frameworks: list[str] = []
    license_statuses: list[str] = []
    redistribution: list[str] = []
    duplicates = 0

    for item in items:
        item_id = str(item.get("id") or "unknown")
        providers.append(str(item.get("provider") or "unknown"))
        kinds.append(str(item.get("kind") or "unknown"))
        item_frameworks = [str(value) for value in item.get("frameworks") or []]
        frameworks.extend(item_frameworks)
        if not item_frameworks:
            no_frameworks.append(item_id)
        if not item.get("product_fit"):
            no_product_fit.append(item_id)
        raw_license = item.get("license")
        license_obj: dict[str, Any] = raw_license if isinstance(raw_license, dict) else {}
        license_statuses.append(str(license_obj.get("status") or "unknown"))
        redistribution.append(str(license_obj.get("redistribution") or "unknown"))
        if item.get("alias_of") or item.get("duplicate_of"):
            duplicates += 1
        raw_dna = item.get("dna")
        dna: dict[str, Any] = raw_dna if isinstance(raw_dna, dict) else {}
        dna_dimensions.extend(str(key) for key, value in dna.items() if value)
        if (
            not str(item.get("name") or "").strip()
            or not str(item.get("description") or "").strip()
            or not item.get("extraction_evidence")
            or item.get("normalization_status") == "manual-required"
        ):
            weak_metadata.append(item_id)
        raw_source = item.get("source")
        source: dict[str, Any] = raw_source if isinstance(raw_source, dict) else {}
        local = source.get("local_path")
        if isinstance(local, str) and local:
            candidate = bank / local
            try:
                resolved = assert_under_v2(bank, candidate)
            except PathEscape:
                missing_local.append(item_id)
            else:
                if not resolved.exists():
                    missing_local.append(item_id)

    quarantine = bank / "quarantine"
    quarantine_count = sum(1 for child in quarantine.iterdir()) if quarantine.is_dir() else 0
    broken_pointers = sum(1 for provider in ("refero", "motionsites") if _pointer_is_broken(bank, provider))
    raw_fts = (lock or {}).get("fts") if isinstance(lock, dict) else None
    fts: dict[str, Any] = raw_fts if isinstance(raw_fts, dict) else {}
    dna_items = sum(1 for item in items if isinstance(item.get("dna"), dict) and any(item["dna"].values()))
    total = len(items)
    health.update(
        {
            "total_assets": total,
            "assets_by_provider": _bounded_counts(providers),
            "assets_by_kind": _bounded_counts(kinds),
            "assets_by_framework": _bounded_counts(frameworks),
            "licenses": _bounded_counts(license_statuses),
            "redistribution": _bounded_counts(redistribution),
            "local_only_count": redistribution.count("local-only"),
            "quarantine_count": quarantine_count,
            "duplicates": duplicates,
            "missing_local_paths": {"count": len(missing_local), "sample_ids": missing_local[:10]},
            "broken_pointers": broken_pointers,
            "catalog_hash_status": "pass",
            "fts": {
                "status": fts.get("status") or "unavailable",
                "schema_version": fts.get("schema_version"),
                "current_schema": fts.get("schema_version") == FTS_SCHEMA_VERSION,
            },
            "dna_coverage": {
                "items": dna_items,
                "total": total,
                "percent": round((dna_items * 100.0 / total), 1) if total else 0.0,
                "dimensions": _bounded_counts(dna_dimensions, limit=20),
            },
            "weak_metadata": {"count": len(weak_metadata), "sample_ids": weak_metadata[:10]},
            "no_product_fit": {"count": len(no_product_fit), "sample_ids": no_product_fit[:10]},
            "no_framework_metadata": {"count": len(no_frameworks), "sample_ids": no_frameworks[:10]},
        }
    )
    return health


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
    if sha256_file(jsonl) != str(lock.get("jsonl_sha256") or ""):
        rows.append(("FAIL", "jsonl", "CATALOG_HASH_MISMATCH"))
        return rows
    rows.append(("PASS", "jsonl", jsonl_name))
    raw_fts = lock.get("fts")
    fts: dict[str, Any] = raw_fts if isinstance(raw_fts, dict) else {}
    fts_status = str(fts.get("status") or "unavailable")
    if fts_status == "available":
        sqlite_name = fts.get("sqlite_filename")
        sqlite_path = bank / "catalog" / str(sqlite_name)
        if sqlite_name and sqlite_path.is_file():
            if sha256_file(sqlite_path) == str(fts.get("sqlite_sha256") or ""):
                if fts.get("schema_version") == FTS_SCHEMA_VERSION:
                    rows.append(("PASS", "fts", "available"))
                else:
                    rows.append(("DEGRADED_FTS", "fts", "schema-old; run rebuild"))
            else:
                rows.append(("FAIL", "fts", "FTS_HASH_MISMATCH"))
        else:
            rows.append(("DEGRADED_FTS", "fts", "sqlite-missing"))
    else:
        rows.append(("DEGRADED_FTS", "fts", fts_status))
    health = bank_health(bank)
    if health.get("catalog_status") != "ok":
        return rows
    rows.extend(
        [
            ("INFO", "assets", str(health["total_assets"])),
            ("INFO", "providers", json.dumps(health["assets_by_provider"], sort_keys=True, separators=(",", ":"))),
            ("INFO", "kinds", json.dumps(health["assets_by_kind"], sort_keys=True, separators=(",", ":"))),
            ("INFO", "frameworks", json.dumps(health["assets_by_framework"], sort_keys=True, separators=(",", ":"))),
            ("INFO", "licenses", json.dumps(health["licenses"], sort_keys=True, separators=(",", ":"))),
            ("INFO", "local-only", str(health["local_only_count"])),
            ("INFO", "duplicates", str(health["duplicates"])),
            ("INFO", "quarantine", str(health["quarantine_count"])),
            (
                "WARN" if health["missing_local_paths"]["count"] else "PASS",
                "local-paths",
                str(health["missing_local_paths"]["count"]),
            ),
            (
                "WARN" if health["broken_pointers"] else "PASS",
                "pointers",
                str(health["broken_pointers"]),
            ),
            ("INFO", "dna-coverage", f"{health['dna_coverage']['percent']}%"),
            ("INFO", "weak-metadata", str(health["weak_metadata"]["count"])),
            ("INFO", "no-product-fit", str(health["no_product_fit"]["count"])),
            ("INFO", "no-framework", str(health["no_framework_metadata"]["count"])),
        ]
    )
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
        "assets": "Design V2 assets",
        "providers": "Design V2 providers",
        "kinds": "Design V2 kinds",
        "frameworks": "Design V2 frameworks",
        "licenses": "Design V2 licenses",
        "local-only": "Design V2 local-only",
        "duplicates": "Design V2 duplicates",
        "quarantine": "Design V2 quarantine",
        "local-paths": "Design V2 local paths",
        "pointers": "Design V2 pointers",
        "dna-coverage": "Design V2 DNA coverage",
        "weak-metadata": "Design V2 weak metadata",
        "no-product-fit": "Design V2 no product fit",
        "no-framework": "Design V2 no framework",
    }
    for status, label, evidence in doctor_rows(root):
        mapped.append((status, labels.get(label, f"Design V2 {label}"), evidence))
    return mapped


def cmd_doctor(root: Path | None = None, *, json_output: bool = False) -> int:
    rows = doctor_rows(root)
    if json_output:
        statuses = {status for status, _label, _evidence in rows}
        overall = "fail" if "FAIL" in statuses else ("degraded" if statuses & {"WARN", "DEGRADED", "DEGRADED_FTS"} else "ok")
        _emit(
            {
                "schema_version": 1,
                "action": "doctor",
                "status": overall,
                "offline": True,
                "checks": [
                    {"status": status, "label": label, "evidence": evidence}
                    for status, label, evidence in rows
                ],
                "health": bank_health(root),
            }
        )
        return 1 if "FAIL" in statuses else 0
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
    frameworks: list[str] | None = None,
    structure_only: bool = False,
    limit: int | None = None,
) -> int:
    return _emit(
        shortlist(
            query,
            root=root,
            intent=intent,
            mode=mode,
            frameworks=frameworks,
            structure_only=structure_only,
            limit=limit,
        )
    )


def dispatch(args: Namespace) -> int:
    action = getattr(args, "design_action", None) or getattr(args, "action", None)
    json_output = bool(getattr(args, "json", False))
    root = Path(args.bank).expanduser() if getattr(args, "bank", None) else None
    try:
        if action == "status":
            return cmd_status(root, json_output=json_output)
        if action == "search":
            query = getattr(args, "query", None) or getattr(args, "target", None)
            if not query:
                return _fail(action, "MISSING_QUERY", "query is required", json_output=json_output, exit_code=2)
            limit = getattr(args, "limit", None)
            if limit is not None and not 1 <= limit <= 50:
                return _fail(action, "INVALID_LIMIT", "limit must be between 1 and 50", json_output=json_output, exit_code=2)
            return cmd_search(
                query,
                kind=getattr(args, "kind", None),
                limit=limit,
                root=root,
                intent=getattr(args, "intent", None),
                mode=getattr(args, "mode", None),
                frameworks=getattr(args, "framework", None),
            )
        if action == "inspect":
            item_id = getattr(args, "target", None)
            if not item_id:
                return _fail(action, "MISSING_ID", "id is required", json_output=json_output, exit_code=2)
            return cmd_inspect(item_id, root=root)
        if action == "rebuild":
            return cmd_rebuild(root, json_output=json_output)
        if action == "doctor":
            return cmd_doctor(root, json_output=json_output)
        if action == "ingest":
            target = getattr(args, "target", None)
            path = _local_input(target) if target else None
            source_id = getattr(args, "source_id", None)
            if path is not None and source_id:
                return _fail(
                    action,
                    "PATH_AND_SOURCE_ID",
                    "choose either LOCAL_PATH or --source-id",
                    json_output=json_output,
                    exit_code=2,
                )
            payload = ingest(
                root,
                provider=getattr(args, "provider", None),
                path=path,
                source_id=source_id,
            )
            return _emit(payload)
        if action == "import":
            target = getattr(args, "target", None)
            if not target:
                return _fail(action, "MISSING_PATH", "local path is required", json_output=json_output, exit_code=2)
            return cmd_import(
                _local_input(target),
                provider=getattr(args, "provider", None) or "manual",
                root=root,
            )
        if action == "sources":
            return cmd_sources(root)
        if action == "shortlist":
            query = getattr(args, "query", None) or getattr(args, "target", None)
            if not query:
                return _fail(action, "MISSING_QUERY", "query is required", json_output=json_output, exit_code=2)
            limit = getattr(args, "limit", None)
            if limit is not None and not 1 <= limit <= 5:
                return _fail(action, "INVALID_LIMIT", "limit must be between 1 and 5", json_output=json_output, exit_code=2)
            return cmd_shortlist(
                query,
                root=root,
                intent=getattr(args, "intent", None),
                mode=getattr(args, "mode", None),
                frameworks=getattr(args, "framework", None),
                structure_only=bool(getattr(args, "structure_only", False)),
                limit=limit,
            )
        if action == "dedupe":
            return _emit(dedupe(root))
    except DesignV2Error as exc:
        return _fail(str(action or "unknown"), exc.code, str(exc), json_output=json_output)
    return _fail("unknown", "UNKNOWN_ACTION", "unknown design action", json_output=json_output, exit_code=2)

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .bank import ensure_layout, resolve_design_v2_root
from .importers.common import write_inbox
from .schema import check_item
from .search import load_catalog


def _inbox_items(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    rows: list[tuple[Path, dict[str, Any]]] = []
    inbox = root / "inbox"
    if not inbox.is_dir():
        return rows
    for path in sorted(inbox.glob("*.json")):
        try:
            item = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            rows.append((path, item))
    return rows


def apply_duplicates(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen_hash: dict[tuple[str, str], str] = {}
    seen_path: dict[str, str] = {}
    id_owner: dict[str, str] = {}
    for item in items:
        if item.get("alias_of") or item.get("duplicate_of"):
            continue
        kind = str(item.get("kind") or "")
        raw_source = item.get("source")
        source: dict[str, Any] = raw_source if isinstance(raw_source, dict) else {}
        digest = str(source.get("content_sha256") or "")
        local = str(source.get("local_path") or "")
        if local and local in seen_path:
            item["duplicate_of"] = seen_path[local]
            item["dedup_reason"] = "path-lineage"
            item["canonical_id"] = seen_path[local]
            continue
        key = (kind, digest)
        if digest and digest != "0" * 64 and key in seen_hash:
            item["duplicate_of"] = seen_hash[key]
            item["dedup_reason"] = "content-hash"
            item["canonical_id"] = seen_hash[key]
            continue
        if digest and digest != "0" * 64:
            seen_hash[key] = str(item["id"])
        if local:
            seen_path[local] = str(item["id"])
        item_id = str(item["id"])
        if item_id in id_owner and id_owner[item_id] != digest:
            suffix = digest[:8] if digest else "dup"
            item["id"] = f"{item_id}-{suffix}"
            item["warnings"] = list(item.get("warnings") or []) + ["DUPLICATE_NORMALIZED_ID"]
            item["dedup_reason"] = "normalized-id"
        else:
            id_owner[item_id] = digest
    return items


def dedupe(root: Path | None = None) -> dict[str, Any]:
    bank = root if root is not None else resolve_design_v2_root()
    ensure_layout(bank)
    combined: list[dict[str, Any]] = []
    catalog_items, _lock, status = load_catalog(bank)
    if status == "ok":
        combined.extend(catalog_items)
    inbox_rows = _inbox_items(bank)
    combined.extend(item for _path, item in inbox_rows)
    before = sum(1 for item in combined if item.get("duplicate_of") or item.get("alias_of"))
    apply_duplicates(combined)
    after = sum(1 for item in combined if item.get("duplicate_of") or item.get("alias_of"))
    written = 0
    for _path, item in inbox_rows:
        if check_item(item):
            continue
        write_inbox(bank, item)
        written += 1
    return {
        "status": "ok",
        "marked": after - before,
        "inbox_written": written,
        "total": len(combined),
    }

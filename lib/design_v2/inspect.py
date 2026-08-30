from __future__ import annotations

from pathlib import Path
from typing import Any

from .bank import PathEscape, assert_under_v2, catalog_ready, resolve_design_v2_root
from .search import load_catalog

MAX_INSPECT_FILES = 64


def inspect_item(item_id: str, *, root: Path | None = None) -> dict[str, Any]:
    bank = root if root is not None else resolve_design_v2_root()
    if not catalog_ready(bank):
        return {"error": "EMPTY", "id": item_id, "packages_loaded": 0}
    items, _lock, status = load_catalog(bank)
    if status != "ok":
        return {"error": status, "id": item_id, "packages_loaded": 0}
    found = next((item for item in items if item.get("id") == item_id), None)
    if found is None:
        return {"error": "NOT_FOUND", "id": item_id, "packages_loaded": 0}
    files: list[str] = []
    file_count = 0
    local_path_status = "not-applicable"
    local = (found.get("source") or {}).get("local_path") if isinstance(found.get("source"), dict) else None
    if isinstance(local, str) and local:
        candidate = bank / local
        try:
            resolved = assert_under_v2(bank, candidate)
        except PathEscape:
            resolved = None
        if resolved is not None and resolved.is_dir():
            local_path_status = "available"
            for child in sorted(resolved.iterdir()):
                if child.is_symlink():
                    continue
                file_count += 1
                if len(files) < MAX_INSPECT_FILES:
                    files.append(child.name)
        else:
            local_path_status = "missing"
    return {
        "id": found.get("id"),
        "kind": found.get("kind"),
        "role": found.get("role"),
        "name": found.get("name"),
        "description": found.get("description"),
        "license": found.get("license"),
        "trust": found.get("trust"),
        "frameworks": found.get("frameworks") or [],
        "product_fit": found.get("product_fit") or [],
        "anti_slop": found.get("anti_slop") or [],
        "extraction_evidence": found.get("extraction_evidence") or [],
        "warnings": found.get("warnings") or [],
        "selection_policy": found.get("selection_policy"),
        "dna": found.get("dna") or {},
        "provenance": found.get("provenance"),
        "source": found.get("source"),
        "files": files,
        "file_count": file_count,
        "files_truncated": file_count > len(files),
        "local_path_status": local_path_status,
        "packages_loaded": 0,
        "untrusted_text": True,
    }

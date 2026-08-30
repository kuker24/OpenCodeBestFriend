from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .bank import PathEscape, assert_under_v2, catalog_ready, resolve_design_v2_root
from .importers.bank_pointer import resolve_catalog_file
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
    preview_status = "not-applicable"
    preview_relative_path = None
    preview_path = None
    catalog_item_id = None
    raw_source = found.get("source")
    source: dict[str, Any] = raw_source if isinstance(raw_source, dict) else {}
    local = source.get("local_path")
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
    raw_provenance = found.get("provenance")
    provenance: dict[str, Any] = raw_provenance if isinstance(raw_provenance, dict) else {}
    upstream = source.get("upstream_id")
    rel = source.get("path")
    if provenance.get("acquisition_method") == "design-bank-pointer":
        catalog_item_id = upstream if isinstance(upstream, str) and upstream else None
        if isinstance(rel, str) and rel:
            preview_relative_path = rel
            preview_status = "missing"
            provider = str(found.get("provider") or source.get("provider") or "")
            pointer_file = bank / "sources" / provider / "pointer.json"
            if pointer_file.is_file() and not pointer_file.is_symlink():
                try:
                    payload = json.loads(pointer_file.read_text(encoding="utf-8"))
                except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                    payload = None
                root = payload.get("root") if isinstance(payload, dict) else None
                if isinstance(root, str):
                    resolved_preview = resolve_catalog_file(Path(root), rel)
                    if resolved_preview is not None and resolved_preview.is_file() and not resolved_preview.is_symlink():
                        preview_status = "available"
                        preview_path = str(resolved_preview)
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
        "catalog_item_id": catalog_item_id,
        "preview_relative_path": preview_relative_path,
        "preview_path": preview_path,
        "preview_status": preview_status,
        "packages_loaded": 0,
        "untrusted_text": True,
    }

from __future__ import annotations

from pathlib import Path
from typing import Any

from .bank import SOURCE_PROVIDERS, atomic_write_json, ensure_layout, resolve_design_v2_root
from .import_stage import import_stage
from .importers import aura, bank_pointer, open_design, user_selected
from .importers.common import IngestRejected


def _ingest_dir(provider: str, folder: Path, bank: Path) -> dict[str, Any]:
    if provider == "aura":
        return aura.ingest(folder, bank)
    if provider == "21st":
        return user_selected.ingest(folder, bank, provider="21st")
    if provider == "github-oss":
        return user_selected.ingest(folder, bank, provider="github-oss")
    if provider == "open-design":
        return open_design.ingest(folder, bank)
    if provider == "manual":
        try:
            aura.inspect(folder)
            return aura.ingest(folder, bank)
        except IngestRejected:
            return user_selected.ingest(folder, bank, provider="manual")
    raise IngestRejected(f"unknown provider {provider}")


def ingest_staged(root: Path, provider: str, source_id: str) -> dict[str, Any]:
    folder = root / "sources" / provider / source_id
    if not folder.is_dir():
        raise IngestRejected("missing_source")
    marker = folder / "ingested.json"
    if marker.is_file():
        return {"status": "skipped", "source_id": source_id, "provider": provider}
    result = _ingest_dir(provider, folder, root)
    atomic_write_json(marker, {"status": "ok", "id": result.get("id"), "source_id": source_id})
    result["source_id"] = source_id
    result["provider"] = provider
    return result


def ingest_path(input_path: Path, root: Path, *, provider: str) -> dict[str, Any]:
    ensure_layout(root)
    if provider in {"refero", "motionsites", "bank-pointer"}:
        return bank_pointer.ingest(input_path, root)
    if provider == "open-design":
        return open_design.ingest(input_path, root)
    src = input_path.expanduser()
    if src.is_dir():
        if provider == "aura":
            aura.inspect(src)
        elif provider in {"21st", "github-oss"}:
            user_selected.inspect(src)
    staged = import_stage(src, root, provider=provider)
    return ingest_staged(root, provider, str(staged["source_id"]))


def ingest_all(root: Path, *, provider: str | None = None) -> dict[str, Any]:
    ensure_layout(root)
    providers = (provider,) if provider else SOURCE_PROVIDERS
    results: list[dict[str, Any]] = []
    if provider in {None, "refero", "motionsites", "bank-pointer"}:
        try:
            results.append(bank_pointer.ingest_discovered(root))
        except IngestRejected:
            pass
    for name in providers:
        if name in {"refero", "motionsites"}:
            continue
        base = root / "sources" / name
        if not base.is_dir():
            continue
        for child in sorted(base.iterdir()):
            if child.is_dir() and child.name not in {".tmp"}:
                results.append(ingest_staged(root, name, child.name))
    return {"status": "ok", "count": len(results), "results": results}


def ingest(root: Path | None = None, *, provider: str | None = None, path: Path | None = None) -> dict[str, Any]:
    bank = root if root is not None else resolve_design_v2_root()
    if path is not None:
        if not provider:
            raise IngestRejected("provider_required")
        return ingest_path(path, bank, provider=provider)
    return ingest_all(bank, provider=provider)

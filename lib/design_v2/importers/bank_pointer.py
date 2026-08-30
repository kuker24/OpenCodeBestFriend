from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..bank import atomic_write_json, ensure_layout
from ..provenance import default_provenance, license_from_evidence
from .common import IngestRejected, catalog_item, dna_from_text, slugify, write_inbox

name = "bank-pointer"

ZERO = "0" * 64


def _load_catalog(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    if isinstance(data, dict):
        items = data.get("items")
        if isinstance(items, list):
            return [row for row in items if isinstance(row, dict)]
    return []


def inspect(path: Path) -> dict[str, Any]:
    refero = path / "Refero" / "bank" / "catalog.json"
    motion = path / "motionsites" / "library" / "catalog.json"
    if not refero.is_file() or not motion.is_file():
        raise IngestRejected("DESIGN_BANK_CATALOGS_MISSING")
    return {
        "provider": name,
        "refero": str(refero),
        "motionsites": str(motion),
        "copied_media": False,
    }


def _visual_item(provider: str, slug: str, name: str, description: str, tags: list[str]) -> dict[str, Any]:
    dna = dna_from_text(name, description, " ".join(tags))
    return catalog_item(
        kind="visual",
        provider=provider,
        slug=slug,
        name=name,
        description=description[:400],
        digest=ZERO,
        local_path="",
        source_type="local",
        dna=dna,
        role="visual",
        frameworks=[],
        provenance=default_provenance(
            provider=provider,
            acquisition_method="design-bank-pointer",
            license_evidence="unknown",
        ),
        license_obj=license_from_evidence(None, "unknown"),
        tags=tags,
        categories=["visual"],
        search_text=" ".join([name, description, " ".join(tags)]),
    )


def ingest(path: Path, bank: Path) -> dict[str, Any]:
    meta = inspect(path)
    ensure_layout(bank)
    atomic_write_json(
        bank / "sources" / "refero" / "pointer.json",
        {"root": str(path), "catalog": "Refero/bank/catalog.json", "copied_media": False},
    )
    atomic_write_json(
        bank / "sources" / "motionsites" / "pointer.json",
        {"root": str(path), "catalog": "motionsites/library/catalog.json", "copied_media": False},
    )
    count = 0
    refero_items = _load_catalog(path / "Refero" / "bank" / "catalog.json")
    for row in refero_items:
        slug = slugify(str(row.get("slug") or row.get("name") or "refero"))
        item = _visual_item(
            "refero",
            slug,
            str(row.get("name") or slug),
            str(row.get("northStar") or row.get("description") or ""),
            [str(t) for t in (row.get("tags") or []) if isinstance(t, str)],
        )
        write_inbox(bank, item)
        count += 1
    motion_items = _load_catalog(path / "motionsites" / "library" / "catalog.json")
    for row in motion_items:
        slug = slugify(str(row.get("id") or row.get("title") or "motion"))
        item = _visual_item(
            "motionsites",
            slug,
            str(row.get("title") or slug),
            str(row.get("jenis") or row.get("page_type") or ""),
            [str(t) for t in (row.get("types_source") or []) if isinstance(t, str)],
        )
        write_inbox(bank, item)
        count += 1
    return {"status": "ok", "count": count, "inspect": meta, "copied_media": False}


def ingest_discovered(bank: Path) -> dict[str, Any]:
    from lib.install import discover_design_bank

    found = discover_design_bank()
    if not found:
        raise IngestRejected("DESIGN_BANK_MISSING")
    return ingest(Path(found[0]), bank)

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any

from ..bank import DesignV2Error
from ..dna import extract_query
from ..provenance import default_provenance
from .common import IngestRejected, detect_anti_slop, write_inbox

name = "open-design"


class LegacyMissing(DesignV2Error):
    code = "OPEN_DESIGN_LEGACY_MISSING"


def _legacy_scripts() -> Path | None:
    here = Path(__file__).resolve()
    repo = here.parents[3]
    clone = repo / "skills" / "impeccable" / "scripts"
    if (clone / "design_intelligence" / "catalog.py").is_file():
        return clone
    from lib.common import config_dir

    installed = config_dir() / "skills" / "impeccable" / "scripts"
    if (installed / "design_intelligence" / "catalog.py").is_file():
        return installed
    return None


def load_legacy():
    scripts = _legacy_scripts()
    if scripts is None:
        raise LegacyMissing("legacy Design Intelligence runtime not found")
    root = str(scripts)
    if root not in sys.path:
        sys.path.insert(0, root)
    return importlib.import_module("design_intelligence.catalog")


def v1_to_v2(item: dict[str, Any]) -> dict[str, Any]:
    out = dict(item)
    out["schema_version"] = 2
    source = dict(item.get("source") or {})
    source.setdefault("type", "archive")
    source.setdefault("retrieval", "offline")
    source.setdefault("provider", "open-design")
    source.setdefault("local_path", "")
    source.setdefault("canonical_url", None)
    source.setdefault("upstream_id", None)
    out["source"] = source
    blob = " ".join(
        [
            str(item.get("name") or ""),
            str(item.get("description") or ""),
            str(item.get("search_text") or ""),
        ]
    )
    extracted = extract_query(blob)
    dna: dict[str, Any] = {}
    for key in (
        "aesthetic", "density", "geometry", "typography", "spacing", "color", "hierarchy", "layout",
        "motion", "interaction", "responsive_behavior", "product_fit", "content_style", "visual_complexity",
        "accessibility",
    ):
        if extracted.get(key):
            dna[key] = extracted[key]
    out["dna"] = dna
    out.setdefault("role", None)
    out.setdefault("frameworks", [])
    out.setdefault("anti_slop", detect_anti_slop(blob))
    out.setdefault("product_fit", list(extracted.get("product_fit") or []))
    raw_lic = item.get("license")
    license_obj: dict[str, Any] = raw_lic if isinstance(raw_lic, dict) else {}
    out["provenance"] = default_provenance(
        provider="open-design",
        acquisition_method="open-design-legacy",
        license_evidence="unknown" if license_obj.get("status") == "unknown" else "declared-only",
        redistribution=license_obj.get("redistribution") or "local-only",
    )
    out["extraction_evidence"] = sorted(
        set(out.get("extraction_evidence") or []) | {f"inferred:dna:{key}" for key in dna}
    )
    out["selection_policy"] = "full-on-selection" if license_obj.get("status") == "known" else "normalized-card-only"
    if license_obj.get("status") == "known":
        out["execution_class"] = "adapted-candidate"
    return out


def inspect(path: Path) -> dict[str, Any]:
    if path.is_file() and path.suffix.lower() == ".zip":
        raise IngestRejected("OPEN_DESIGN_BANK_REQUIRED")
    lock = path / "catalog" / "catalog.lock.json"
    if not lock.is_file():
        raise IngestRejected("OPEN_DESIGN_BANK_REQUIRED")
    return {"provider": name, "bank": str(path), "lock": True}


def ingest(path: Path, bank: Path) -> dict[str, Any]:
    inspect(path)
    catalog = load_legacy()
    items = catalog.load_items(path)
    written = 0
    ids: list[str] = []
    for row in items:
        converted = v1_to_v2(row)
        write_inbox(bank, converted)
        written += 1
        ids.append(str(converted.get("id") or ""))
    return {"status": "ok", "count": written, "ids": ids[:32]}

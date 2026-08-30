from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..bank import atomic_write_json, ensure_layout
from ..provenance import default_provenance, license_from_evidence
from ..schema import REL_PATH_RE
from .common import IngestRejected, KIND_DIR, catalog_item, detect_anti_slop, dna_from_text, slugify, write_inbox

name = "bank-pointer"

ZERO = "0" * 64
CATALOG_PROVIDERS = frozenset({"21st", "aura"})
POINTER_PROVIDERS = ("refero", "motionsites", "21st", "aura")
POINTER_PREVIEW_SAMPLE = 5
PREVIEW_STILLS = {".webp", ".png", ".jpg", ".jpeg", ".avif"}
JENIS_KIND = {
    "shader": "effect",
    "theme": "theme",
    "template": "template",
    "landing-page": "page",
    "3d-website": "page",
    "mobile-app": "page",
    "hero": "section",
    "features": "section",
    "footer": "section",
    "cta": "section",
    "pricing": "section",
    "about": "section",
    "blog": "section",
    "carousel": "section",
    "stats": "section",
    "testimonials": "section",
    "404": "section",
    "button": "component",
    "card": "component",
    "form": "component",
    "nav": "component",
    "navbar": "component",
    "input": "component",
    "modal": "component",
    "tabs": "component",
    "accordion": "component",
    "badge": "component",
    "dropdown": "component",
}


def map_jenis_kind(jenis: str, catalog_kind: str | None = None) -> str:
    key = (jenis or "").strip().lower()
    mapped = JENIS_KIND.get(key)
    if mapped:
        return mapped
    if catalog_kind and catalog_kind in KIND_DIR:
        return catalog_kind
    return "pattern"


def catalog_json_path(path: Path) -> Path:
    return path.expanduser() / "library" / "catalog.json"


def has_catalog_json(path: Path) -> bool:
    catalog = catalog_json_path(path)
    return catalog.is_file() and not catalog.is_symlink()


def is_catalog_bank(path: Path) -> bool:
    if not has_catalog_json(path):
        return False
    try:
        data = json.loads(catalog_json_path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return False
    return isinstance(data, dict) and isinstance(data.get("items"), list)


def preview_relative_path(row: dict[str, Any]) -> str:
    item_id = str(row.get("id") or "").strip()
    jenis = str(row.get("jenis") or "").strip()
    raw = row.get("preview")
    preview = raw.strip() if isinstance(raw, str) else ""
    if not preview:
        return ""
    candidate = Path(preview)
    if candidate.is_absolute() or ".." in candidate.parts:
        return ""
    if len(candidate.parts) == 1:
        if not item_id or not jenis:
            return ""
        rel = f"library/{jenis}/{item_id}/{preview}"
    else:
        rel = candidate.as_posix()
    if Path(rel).suffix.lower() not in PREVIEW_STILLS:
        return ""
    if not REL_PATH_RE.fullmatch(rel) or ".." in Path(rel).parts:
        return ""
    return rel


def resolve_catalog_file(root: Path, relative: str) -> Path | None:
    rel = Path(relative)
    if not relative or rel.is_absolute() or ".." in rel.parts:
        return None
    try:
        base = root.expanduser().resolve()
    except OSError:
        return None
    candidate = base / rel
    if candidate.is_symlink():
        return None
    try:
        resolved = candidate.resolve()
        resolved.relative_to(base)
    except (OSError, ValueError):
        return None
    return resolved


def pointer_catalog_rows(data: Any, provider: str) -> list[dict[str, Any]] | None:
    raw: list[Any]
    if provider in CATALOG_PROVIDERS:
        if not isinstance(data, dict) or not isinstance(data.get("items"), list):
            return None
        raw = data["items"]
    elif isinstance(data, list):
        raw = data
    elif isinstance(data, dict):
        found: list[Any] | None = None
        for key in ("items", "styles"):
            value = data.get(key)
            if isinstance(value, list):
                found = value
                break
        if found is None:
            return None
        raw = found
    else:
        return None
    if any(not isinstance(row, dict) for row in raw):
        return None
    return raw


def _load_catalog(path: Path) -> list[dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return []
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    if isinstance(data, dict):
        for key in ("items", "styles"):
            rows = data.get(key)
            if isinstance(rows, list):
                return [row for row in rows if isinstance(row, dict)]
    return []


def _load_provider_catalog(path: Path) -> list[dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IngestRejected("MALFORMED_CATALOG") from exc
    if isinstance(data, dict):
        items = data.get("items")
        if isinstance(items, list):
            return [row for row in items if isinstance(row, dict)]
    raise IngestRejected("MALFORMED_CATALOG")


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


def _pointer_item(
    *,
    kind: str,
    provider: str,
    slug: str,
    name: str,
    description: str,
    tags: list[str],
    categories: list[str],
    role: str,
    upstream_id: str | None = None,
    source_path: str = "",
) -> dict[str, Any]:
    text = " ".join([name, description, " ".join(tags), " ".join(categories)])
    dna = dna_from_text(name, description, " ".join(tags), " ".join(categories))
    item = catalog_item(
        kind=kind,
        provider=provider,
        slug=slug,
        name=name[:160],
        description=description[:400],
        digest=ZERO,
        local_path="",
        source_type="local",
        dna=dna,
        role=role,
        frameworks=[],
        provenance=default_provenance(
            provider=provider,
            acquisition_method="design-bank-pointer",
            license_evidence="unknown",
        ),
        license_obj=license_from_evidence(None, "unknown"),
        tags=tags,
        categories=categories,
        search_text=text[:1200],
        anti_slop=detect_anti_slop(text),
        extraction_evidence=["detected:source:legacy-design-bank-pointer", f"inferred:kind:{kind}"]
        + [f"inferred:dna:{key}" for key in sorted(dna)],
        warnings=["LICENSE_UNKNOWN", "FRAMEWORK_UNKNOWN"] + ([] if dna.get("product_fit") else ["PRODUCT_FIT_UNKNOWN"]),
    )
    item["source"]["upstream_id"] = upstream_id
    item["source"]["path"] = source_path
    item["source"]["local_path"] = ""
    return item


def _visual_item(provider: str, slug: str, name: str, description: str, tags: list[str]) -> dict[str, Any]:
    return _pointer_item(
        kind="visual",
        provider=provider,
        slug=slug,
        name=name,
        description=description,
        tags=tags,
        categories=["visual"],
        role="visual",
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


def ingest_catalog_bank(path: Path, bank: Path, *, provider: str) -> dict[str, Any]:
    if provider not in CATALOG_PROVIDERS:
        raise IngestRejected("provider")
    root = path.expanduser()
    catalog = root / "library" / "catalog.json"
    if catalog.is_symlink() or not catalog.is_file():
        raise IngestRejected("CATALOG_MISSING")
    rows = _load_provider_catalog(catalog)
    ensure_layout(bank)
    atomic_write_json(
        bank / "sources" / provider / "pointer.json",
        {
            "root": str(root.resolve()),
            "catalog": "library/catalog.json",
            "copied_media": False,
        },
    )
    count = 0
    for row in rows:
        item_id = str(row.get("id") or "").strip()
        if not item_id:
            continue
        jenis = str(row.get("jenis") or "").strip()
        raw_kind = row.get("kind")
        catalog_kind = raw_kind if isinstance(raw_kind, str) else None
        kind = map_jenis_kind(jenis, catalog_kind)
        raw_title = row.get("title") or row.get("name")
        title = raw_title if isinstance(raw_title, str) and raw_title.strip() else item_id
        raw_desc = row.get("description")
        description = raw_desc if isinstance(raw_desc, str) and raw_desc.strip() else jenis
        tags = [str(tag) for tag in (row.get("tags") or []) if isinstance(tag, str)]
        if jenis and jenis not in tags:
            tags.append(jenis)
        categories = [jenis] if jenis else [kind]
        item = _pointer_item(
            kind=kind,
            provider=provider,
            slug=slugify(item_id),
            name=title,
            description=description or title,
            tags=tags,
            categories=categories,
            role=kind,
            upstream_id=item_id,
            source_path=preview_relative_path(row),
        )
        write_inbox(bank, item)
        count += 1
    return {
        "status": "ok",
        "count": count,
        "provider": provider,
        "copied_media": False,
        "inspect": {
            "provider": provider,
            "catalog": str(catalog),
            "copied_media": False,
        },
    }


def ingest_discovered(bank: Path) -> dict[str, Any]:
    from lib.install import discover_design_bank

    found = discover_design_bank()
    if not found:
        raise IngestRejected("DESIGN_BANK_MISSING")
    return ingest(Path(found[0]), bank)

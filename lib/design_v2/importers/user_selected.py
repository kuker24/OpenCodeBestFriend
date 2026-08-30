from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..bank import assert_under_v2, atomic_write_json, ensure_layout
from ..provenance import default_provenance, license_from_evidence
from .common import (
    IngestRejected,
    KIND_DIR,
    catalog_item,
    copy_tree_filtered,
    detect_license,
    dna_from_text,
    guess_kind_role,
    slugify,
    tree_digest,
    write_inbox,
)

name = "21st"

MARKET_MEDIA = {".gif", ".mp4", ".webm", ".mov"}
SCRAPE_KEYS = {
    "previewurl",
    "preview_url",
    "videourl",
    "thumbnailurl",
    "weeklydownloads",
    "21st.dev",
}
HTML_MARKERS = (
    "copy prompt",
    "21st.dev/community",
    "the living library",
)


def _files(folder: Path) -> list[Path]:
    out: list[Path] = []
    for path in folder.rglob("*"):
        if path.is_file() and not path.is_symlink():
            out.append(path)
    return out


def _is_scrape_json(path: Path) -> bool:
    if path.suffix.lower() != ".json":
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace")[:200000])
    except json.JSONDecodeError:
        return False
    rows = data if isinstance(data, list) else [data]
    if not rows or not isinstance(rows[0], dict):
        return False
    hits = 0
    for row in rows[:20]:
        keys = {str(k).lower() for k in row}
        if keys & SCRAPE_KEYS:
            hits += 1
    return hits >= 3 or (len(rows) > 5 and hits >= 1)


def _is_marketplace_html(path: Path) -> bool:
    if path.suffix.lower() not in {".html", ".htm"}:
        return False
    text = path.read_text(encoding="utf-8", errors="replace")[:20000].lower()
    return sum(1 for marker in HTML_MARKERS if marker in text) >= 2


def inspect(path: Path) -> dict[str, Any]:
    folder = path if path.is_dir() else path.parent
    files = _files(folder)
    if not files:
        raise IngestRejected("empty")
    media = [p for p in files if p.suffix.lower() in MARKET_MEDIA or "thumbnail" in p.name.lower() or "preview" in p.name.lower()]
    source = [
        p
        for p in files
        if p.suffix.lower() in {".tsx", ".jsx", ".ts", ".js", ".mjs", ".html", ".css", ".md"}
        and p.name.lower() not in {"license.md"}
    ]
    if any(_is_scrape_json(p) for p in files):
        raise IngestRejected("MARKETPLACE_SCRAPE_JSON")
    if any(_is_marketplace_html(p) for p in files):
        raise IngestRejected("MARKETPLACE_HTML")
    if len(media) >= 5 and not source:
        raise IngestRejected("MARKETPLACE_MEDIA_DUMP")
    if not source:
        raise IngestRejected("NO_SOURCE_FILES")
    return {"provider": name, "source_files": len(source), "media_skipped": len(media)}


def ingest(path: Path, bank: Path, *, provider: str = "21st") -> dict[str, Any]:
    folder = path if path.is_dir() else path.parent
    meta = inspect(folder)
    files = _files(folder)
    names = [p.name.lower() for p in files]
    text = ""
    for path_f in files:
        if path_f.suffix.lower() in {".md", ".tsx", ".jsx", ".html"}:
            text += path_f.read_text(encoding="utf-8", errors="replace")[:1500]
    kind, role = guess_kind_role(names, text)
    slug = slugify(folder.name)
    if slug in {"payload", "21st", "item"}:
        slug = slugify(next((p.stem for p in files if p.suffix.lower() in {".tsx", ".jsx", ".html"}), "selected"))
    dna = dna_from_text(text, slug)
    spdx, evidence = detect_license(folder)
    license_obj = license_from_evidence(spdx, evidence)
    frameworks: list[str] = []
    if any(p.suffix.lower() in {".tsx", ".jsx"} for p in files):
        frameworks.extend(["react", "tailwind"])
    if any(p.suffix.lower() == ".html" for p in files):
        frameworks.append("html")
    ensure_layout(bank)
    dest = bank / KIND_DIR[kind] / provider / slug
    assert_under_v2(bank, dest)
    copied = copy_tree_filtered(folder, dest, skip_suffixes=MARKET_MEDIA)
    digest = tree_digest(dest)
    local_path = f"{KIND_DIR[kind]}/{provider}/{slug}"
    provenance = default_provenance(
        provider=provider,
        acquisition_method="official-user-selected-export",
        license_evidence=evidence,
        marketplace_metadata_copied=False,
        marketplace_media_copied=False,
    )
    item = catalog_item(
        kind=kind,
        provider=provider,
        slug=slug,
        name=slug.replace("-", " "),
        description=(text.split("\n", 1)[0] if text else f"User-selected {provider} {slug}")[:400],
        digest=digest,
        local_path=local_path,
        source_type="user-export",
        dna=dna,
        role=role,
        frameworks=frameworks,
        provenance=provenance,
        license_obj=license_obj,
        tags=[provider],
        categories=[role] if role else [],
        search_text=" ".join([slug, text[:400]]),
    )
    atomic_write_json(dest / "manifest.json", item)
    atomic_write_json(dest / "dna.json", dna)
    atomic_write_json(dest / "provenance.json", provenance)
    inbox = write_inbox(bank, item)
    return {
        "status": "ok",
        "id": item["id"],
        "path": local_path,
        "inbox": str(inbox),
        "inspect": meta,
        "copied": copied,
    }

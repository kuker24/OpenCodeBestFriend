from __future__ import annotations

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

name = "aura"


def _names(folder: Path) -> list[str]:
    names: list[str] = []
    for path in folder.rglob("*"):
        if path.is_file() and not path.is_symlink():
            names.append(path.name.lower())
    return names


def inspect(path: Path) -> dict[str, Any]:
    folder = path if path.is_dir() else path.parent
    names = _names(folder)
    has_html = any(n.endswith(".html") for n in names)
    has_design = "design.md" in names
    has_manifest = "manifest.json" in names
    if not (has_html or has_design or has_manifest):
        raise IngestRejected("UNKNOWN_AURA_LAYOUT")
    return {
        "provider": name,
        "html": has_html,
        "design_md": has_design,
        "manifest": has_manifest,
        "files": len(names),
    }


def ingest(path: Path, bank: Path) -> dict[str, Any]:
    folder = path if path.is_dir() else path.parent
    meta = inspect(folder)
    names = _names(folder)
    design_text = ""
    design_path = folder / "DESIGN.md"
    if not design_path.is_file():
        for cand in folder.rglob("DESIGN.md"):
            if cand.is_file() and not cand.is_symlink():
                design_path = cand
                break
    if design_path.is_file() and not design_path.is_symlink():
        design_text = design_path.read_text(encoding="utf-8", errors="replace")[:4000]
    html_text = ""
    for cand in folder.rglob("*.html"):
        if cand.is_file() and not cand.is_symlink():
            html_text += cand.read_text(encoding="utf-8", errors="replace")[:2000]
            break
    kind, role = guess_kind_role(names, design_text + " " + html_text)
    slug = slugify(folder.name if folder.name not in {"payload", "aura"} else (design_text.split("\n", 1)[0] or "export"))
    if slug in {"payload", "item"}:
        slug = slugify(next((n[:-5] for n in names if n.endswith(".html")), "aura-export"))
    dna = dna_from_text(design_text, html_text, slug)
    spdx, evidence = detect_license(folder)
    license_obj = license_from_evidence(spdx, evidence)
    frameworks: list[str] = []
    if any(n.endswith(".html") for n in names):
        frameworks.append("html")
    if any(n.endswith(".css") for n in names):
        frameworks.append("css")
    if any(n.endswith(".js") or n.endswith(".mjs") for n in names):
        frameworks.append("javascript")
    ensure_layout(bank)
    dest = bank / KIND_DIR[kind] / "aura" / slug
    assert_under_v2(bank, dest)
    copied = copy_tree_filtered(folder, dest)
    digest = tree_digest(dest)
    local_path = f"{KIND_DIR[kind]}/aura/{slug}"
    provenance = default_provenance(
        provider="aura",
        acquisition_method="official-user-export",
        license_evidence=evidence,
    )
    item = catalog_item(
        kind=kind,
        provider="aura",
        slug=slug,
        name=slug.replace("-", " "),
        description=(design_text.split("\n", 1)[0] if design_text else f"Aura export {slug}")[:400],
        digest=digest,
        local_path=local_path,
        source_type="user-export",
        dna=dna,
        role=role,
        frameworks=frameworks,
        provenance=provenance,
        license_obj=license_obj,
        tags=["aura"],
        categories=[role] if role else [],
        search_text=" ".join([slug, design_text[:400], " ".join(copied)]),
    )
    atomic_write_json(dest / "manifest.json", item)
    atomic_write_json(dest / "dna.json", dna)
    atomic_write_json(dest / "provenance.json", provenance)
    inbox = write_inbox(bank, item)
    return {"status": "ok", "id": item["id"], "path": local_path, "inbox": str(inbox), "inspect": meta}

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
    detect_anti_slop,
    detect_frameworks,
    detect_license,
    dna_from_text,
    guess_kind_role,
    slugify,
    staged_provenance,
    tree_digest,
    write_inbox,
)

name = "aura"
MANIFEST_FIELDS = {
    "name",
    "description",
    "kind",
    "role",
    "frameworks",
    "categories",
    "tags",
    "product_fit",
    "intent",
    "modes",
    "anti_slop",
    "dna",
}


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(entry) for entry in value if isinstance(entry, str) and entry.strip()]


def _user_manifest(folder: Path) -> tuple[dict[str, Any], list[str]]:
    explicit = folder / "design-v2.json"
    fallback = folder / "manifest.json"
    path = explicit if explicit.is_file() else fallback
    if not path.is_file() or path.is_symlink():
        return {}, []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        if path == explicit:
            raise IngestRejected("MALFORMED_AURA_MANIFEST") from exc
        return {}, []
    if path == fallback:
        if not isinstance(raw, dict) or not isinstance(raw.get("opencode_design_v2"), dict):
            return {}, []
        raw = raw["opencode_design_v2"]
    if not isinstance(raw, dict):
        raise IngestRejected("MALFORMED_AURA_MANIFEST")
    manifest = {key: raw[key] for key in MANIFEST_FIELDS if key in raw}
    for key in ("name", "description", "kind", "role"):
        if key in manifest and not isinstance(manifest[key], str):
            raise IngestRejected(f"MALFORMED_AURA_MANIFEST:{key}")
    if "kind" in manifest and manifest["kind"] not in KIND_DIR:
        raise IngestRejected("MALFORMED_AURA_MANIFEST:kind")
    for key in ("frameworks", "categories", "tags", "product_fit", "intent", "modes", "anti_slop"):
        if key in manifest and (
            not isinstance(manifest[key], list)
            or any(not isinstance(entry, str) for entry in manifest[key])
        ):
            raise IngestRejected(f"MALFORMED_AURA_MANIFEST:{key}")
    if "dna" in manifest:
        dna = manifest["dna"]
        if not isinstance(dna, dict) or any(
            not isinstance(value, str)
            and not (isinstance(value, list) and all(isinstance(entry, str) for entry in value))
            for value in (dna.values() if isinstance(dna, dict) else [])
        ):
            raise IngestRejected("MALFORMED_AURA_MANIFEST:dna")
    evidence = [f"user-declared:{key}" for key in sorted(manifest)]
    return manifest, evidence


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
    manifest, _evidence = _user_manifest(folder)
    has_manifest = bool(manifest)
    if not (has_html or has_design or has_manifest):
        raise IngestRejected("UNKNOWN_AURA_LAYOUT")
    return {
        "provider": name,
        "html": has_html,
        "design_md": has_design,
        "manifest": has_manifest,
        "files": len(names),
    }


def ingest(path: Path, bank: Path, *, provider: str = "aura") -> dict[str, Any]:
    folder = path if path.is_dir() else path.parent
    meta = inspect(folder)
    names = _names(folder)
    manifest, manifest_evidence = _user_manifest(folder)
    source_provenance = staged_provenance(folder, provider)
    design_text = ""
    design_path = folder / "DESIGN.md"
    if not design_path.is_file():
        for cand in folder.rglob("DESIGN.md"):
            if cand.is_file() and not cand.is_symlink():
                design_path = cand
                break
    if design_path.is_file() and not design_path.is_symlink():
        design_text = design_path.read_text(encoding="utf-8", errors="replace")[:4000]
    source_text = ""
    for cand in sorted(folder.rglob("*")):
        if len(source_text) >= 6000:
            break
        if cand.is_file() and not cand.is_symlink() and cand.suffix.lower() in {".html", ".css", ".js", ".mjs"}:
            source_text += cand.read_text(encoding="utf-8", errors="replace")[:1500]
    inference_text = design_text + " " + source_text
    inferred_kind, inferred_role = guess_kind_role(names, inference_text)
    declared_kind = manifest.get("kind")
    kind = str(declared_kind) if isinstance(declared_kind, str) and declared_kind in KIND_DIR else inferred_kind
    role = str(manifest.get("role")) if isinstance(manifest.get("role"), str) else inferred_role
    declared_name = str(manifest.get("name") or "").strip()
    heading = design_text.split("\n", 1)[0].lstrip("# ").strip()
    source_name = str(source_provenance.get("source_name") or "").strip()
    slug = slugify(
        declared_name
        or source_name
        or (folder.name if folder.name not in {"payload", "aura"} else (heading or "export"))
    )
    if slug in {"payload", "item"}:
        slug = slugify(next((n[:-5] for n in names if n.endswith(".html")), "aura-export"))
    dna = dna_from_text(design_text, source_text, declared_name, slug)
    declared_dna = manifest.get("dna")
    if isinstance(declared_dna, dict):
        for key, value in declared_dna.items():
            if key in dna or key in {
                "aesthetic", "density", "geometry", "typography", "spacing", "color", "hierarchy",
                "layout", "motion", "interaction", "responsive_behavior", "product_fit", "content_style",
                "visual_complexity", "accessibility",
            }:
                if isinstance(value, str) or (
                    isinstance(value, list) and all(isinstance(entry, str) for entry in value)
                ):
                    dna[key] = value
    spdx, evidence = detect_license(folder)
    license_obj = license_from_evidence(spdx, evidence)
    files = [candidate for candidate in folder.rglob("*") if candidate.is_file() and not candidate.is_symlink()]
    frameworks, framework_evidence = detect_frameworks(files, inference_text)
    declared_frameworks = _string_list(manifest.get("frameworks"))
    frameworks = sorted(set(frameworks) | set(declared_frameworks))
    ensure_layout(bank)
    dest = bank / KIND_DIR[kind] / provider / slug
    assert_under_v2(bank, dest)
    copied = copy_tree_filtered(folder, dest)
    digest = tree_digest(dest)
    local_path = f"{KIND_DIR[kind]}/{provider}/{slug}"
    provenance = default_provenance(**source_provenance)
    provenance.update(
        {
            "provider": provider,
            "acquisition_method": "official-user-export" if provider == "aura" else "user-selected-local-source",
            "license_evidence": evidence,
        }
    )
    anti_slop = sorted(set(detect_anti_slop(inference_text)) | set(_string_list(manifest.get("anti_slop"))))
    product_fit = sorted(set(dna.get("product_fit") or []) | set(_string_list(manifest.get("product_fit"))))
    extraction_evidence = manifest_evidence + framework_evidence
    if "kind" not in manifest:
        extraction_evidence.append(f"inferred:kind:{kind}")
    if "role" not in manifest:
        extraction_evidence.append(f"inferred:role:{role}")
    extraction_evidence.extend(f"inferred:dna:{key}" for key in sorted(dna) if f"user-declared:dna" not in manifest_evidence)
    warnings: list[str] = []
    if license_obj.get("status") == "unknown":
        warnings.append("LICENSE_UNKNOWN")
    if not frameworks:
        warnings.append("FRAMEWORK_UNKNOWN")
    if not product_fit:
        warnings.append("PRODUCT_FIT_UNKNOWN")
    description = str(manifest.get("description") or heading or f"Aura export {slug}").strip()
    item = catalog_item(
        kind=kind,
        provider=provider,
        slug=slug,
        name=(declared_name or slug.replace("-", " "))[:160],
        description=description[:400],
        digest=digest,
        local_path=local_path,
        source_type="user-export" if provider == "aura" else "manual",
        dna=dna,
        role=role,
        frameworks=frameworks,
        provenance=provenance,
        license_obj=license_obj,
        tags=sorted(set([provider] + _string_list(manifest.get("tags")))),
        categories=sorted(set(([role] if role else []) + _string_list(manifest.get("categories")))),
        search_text=" ".join([slug, design_text[:400], " ".join(copied)]),
        anti_slop=anti_slop,
        product_fit=product_fit,
        extraction_evidence=extraction_evidence,
        warnings=warnings,
        source_id=str(source_provenance.get("source_id") or "") or None,
        intent=_string_list(manifest.get("intent")),
        modes=_string_list(manifest.get("modes")),
    )
    atomic_write_json(dest / "manifest.json", item)
    atomic_write_json(dest / "dna.json", dna)
    atomic_write_json(dest / "provenance.json", provenance)
    inbox = write_inbox(bank, item)
    return {"status": "ok", "id": item["id"], "path": local_path, "inbox": str(inbox), "inspect": meta}

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import tempfile
import uuid
from pathlib import Path
from typing import Any

from ..bank import DesignV2Error, assert_under_v2, atomic_write_json, ensure_layout, load_policy
from ..dna import extract_query
from ..provenance import load_provenance
from ..schema import empty_item_v2
from ..security import allowed_extension

KIND_DIR = {
    "system": "systems",
    "structure": "templates",
    "recipe": "patterns",
    "specialist": "patterns",
    "visual": "patterns",
    "component": "components",
    "primitive": "primitives",
    "block": "blocks",
    "section": "sections",
    "page": "pages",
    "template": "templates",
    "theme": "themes",
    "motion": "motion",
    "effect": "effects",
    "background": "backgrounds",
    "pattern": "patterns",
}

SLUG_RE = re.compile(r"[^a-z0-9]+")
DNA_DIMENSIONS = (
    "aesthetic",
    "density",
    "geometry",
    "typography",
    "spacing",
    "color",
    "hierarchy",
    "layout",
    "motion",
    "interaction",
    "responsive_behavior",
    "product_fit",
    "content_style",
    "visual_complexity",
    "accessibility",
)
ANTI_SLOP_PHRASES = {
    "giant gradient headline": "giant-gradient-title",
    "giant gradient title": "giant-gradient-title",
    "excessive glass": "excessive-glassmorphism",
    "excessive glassmorphism": "excessive-glassmorphism",
    "excessive glow": "excessive-glow",
    "floating blob": "floating-gradient-blobs",
    "floating gradient blob": "floating-gradient-blobs",
    "random bento": "random-bento",
    "pill everything": "pill-everything",
    "pill-everything": "pill-everything",
    "meaningless dashboard card": "meaningless-dashboard-cards",
    "huge radius": "huge-radius",
    "generic saas hero": "generic-saas-hero",
    "over animation": "over-animation",
    "over-animation": "over-animation",
    "fake metric": "fake-metrics",
    "decorative chart": "decorative-charts",
}


class IngestRejected(DesignV2Error):
    code = "INGEST_REJECTED"


def slugify(text: str) -> str:
    slug = SLUG_RE.sub("-", text.lower()).strip("-")
    return slug[:64] or "item"


def make_id(kind: str, provider: str, slug: str) -> str:
    prov = slugify(provider)
    return f"{kind}:{prov}-{slugify(slug)}"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_digest(root: Path) -> str:
    h = hashlib.sha256()
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames.sort()
        for name in sorted(filenames):
            path = Path(dirpath) / name
            if path.is_symlink() or name == "provenance.json":
                continue
            rel = path.relative_to(root).as_posix()
            h.update(rel.encode("utf-8"))
            h.update(sha256_file(path).encode("ascii"))
    return h.hexdigest()


def detect_license(folder: Path) -> tuple[str | None, str]:
    policy = load_policy()
    signatures = policy.get("license_signatures") or {}
    text = ""
    for name in ("LICENSE", "LICENSE.txt", "LICENSE.md", "COPYING"):
        path = folder / name
        if path.is_file() and not path.is_symlink():
            text = path.read_text(encoding="utf-8", errors="replace")[:8000]
            break
    if not text:
        return None, "unknown"
    for spdx, rules in signatures.items():
        required = list(rules.get("required") or [])
        if required and all(part.lower() in text.lower() for part in required):
            return str(spdx), "signature"
    return None, "unknown"


def guess_kind_role(names: list[str], text: str) -> tuple[str, str]:
    blob = " ".join(names).lower() + " " + text.lower()
    if any(w in blob for w in ("button", "input", "combobox", "checkbox")):
        return "component", "control"
    if any(w in blob for w in ("navbar", "nav", "header", "footer", "sidebar")):
        return "block", "chrome"
    if any(w in blob for w in ("hero",)):
        return "section", "hero"
    if any(w in blob for w in ("pricing", "testimonial", "feature")):
        return "section", "section"
    if any(w in blob for w in ("dashboard", "page")):
        return "page", "page"
    if "design.md" in blob and not any(n.endswith(".html") for n in names):
        return "system", "system"
    return "section", "section"


def dna_from_text(*parts: str) -> dict[str, Any]:
    extracted = extract_query(" ".join(p for p in parts if p))
    dna: dict[str, Any] = {}
    for key in DNA_DIMENSIONS:
        if extracted.get(key):
            dna[key] = extracted[key]
    return dna


def detect_anti_slop(text: str) -> list[str]:
    lowered = text.lower().replace("_", " ").replace("-", " ")
    flags = {flag for phrase, flag in ANTI_SLOP_PHRASES.items() if phrase.replace("-", " ") in lowered}
    if "gradient" in lowered and "purple" in lowered and "blue" in lowered:
        flags.add("purple-blue-gradient")
    if text.lower().count("rounded-full") >= 3:
        flags.add("pill-everything")
    if text.lower().count("backdrop-blur") >= 3:
        flags.add("excessive-glassmorphism")
    if text.lower().count("rounded-3xl") >= 4:
        flags.add("huge-radius")
    if text.lower().count("animate-") >= 5:
        flags.add("over-animation")
    return sorted(flags)


def detect_frameworks(files: list[Path], text: str) -> tuple[list[str], list[str]]:
    names = {path.name.lower() for path in files}
    suffixes = {path.suffix.lower() for path in files}
    lowered = text.lower()
    frameworks: set[str] = set()
    evidence: list[str] = []
    if suffixes & {".tsx", ".jsx"} or "from 'react'" in lowered or 'from "react"' in lowered:
        frameworks.add("react")
        evidence.append("detected:framework:react")
    tailwind_config = any(name.startswith("tailwind.config.") for name in names)
    tailwind_classes = bool(re.search(r"class(?:name)?\s*=.{0,120}\b(?:bg-|text-|grid|flex|p[trblxy]?--?\d|m[trblxy]?--?\d|rounded-)", text, re.IGNORECASE))
    package = next((path for path in files if path.name.lower() == "package.json"), None)
    tailwind_dependency = False
    if package is not None:
        try:
            data = json.loads(package.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            data = {}
        if isinstance(data, dict):
            dependencies = {
                str(key).lower()
                for section in ("dependencies", "devDependencies", "peerDependencies")
                for key in ((data.get(section) or {}) if isinstance(data.get(section), dict) else {})
            }
            tailwind_dependency = "tailwindcss" in dependencies
    if tailwind_config or tailwind_classes or tailwind_dependency:
        frameworks.add("tailwind")
        evidence.append("detected:framework:tailwind")
    if ".html" in suffixes:
        frameworks.add("html")
        evidence.append("detected:framework:html")
    if ".css" in suffixes:
        frameworks.add("css")
        evidence.append("detected:framework:css")
    if suffixes & {".js", ".mjs"}:
        frameworks.add("javascript")
        evidence.append("detected:framework:javascript")
    return sorted(frameworks), evidence


def staged_provenance(folder: Path, provider: str) -> dict[str, Any]:
    return load_provenance(folder, expected_provider=provider)


def copy_tree_filtered(src: Path, dest: Path, *, skip_suffixes: set[str] | None = None) -> list[str]:
    policy = load_policy()
    skip = {s.lower() for s in (skip_suffixes or set())}
    copied: list[str] = []
    dest.parent.mkdir(parents=True, exist_ok=True)
    staged = Path(tempfile.mkdtemp(prefix=f".{dest.name}-incoming-", dir=str(dest.parent)))
    backup = dest.parent / f".{dest.name}-backup-{uuid.uuid4().hex}"
    try:
        for dirpath, dirnames, filenames in os.walk(src, followlinks=False):
            current = Path(dirpath)
            if current.is_symlink():
                raise IngestRejected("symlink")
            rel = current.relative_to(src)
            target_dir = staged / rel if str(rel) != "." else staged
            kept: list[str] = []
            for name in dirnames:
                child = current / name
                st = child.lstat()
                if stat.S_ISLNK(st.st_mode) or not stat.S_ISDIR(st.st_mode):
                    raise IngestRejected("unsafe_directory")
                kept.append(name)
                (target_dir / name).mkdir(parents=True, exist_ok=True)
            dirnames[:] = kept
            for name in filenames:
                if name in {"provenance.json", "ingested.json"}:
                    continue
                child = current / name
                st = child.lstat()
                if stat.S_ISLNK(st.st_mode) or st.st_nlink > 1 or not stat.S_ISREG(st.st_mode):
                    raise IngestRejected("unsafe_file")
                suffix = Path(name).suffix.lower()
                if suffix in skip:
                    continue
                if not allowed_extension(name, policy) and name.lower() not in {"license", "copying", "design.md"}:
                    continue
                out = target_dir / name
                assert_under_v2(staged, out)
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(child, out)
                copied.append(str((rel / name) if str(rel) != "." else Path(name)))
        if dest.exists():
            if dest.is_symlink() or not dest.is_dir():
                raise IngestRejected("unsafe_destination")
            os.replace(dest, backup)
        try:
            os.replace(staged, dest)
        except Exception:
            if backup.exists() and not dest.exists():
                os.replace(backup, dest)
            raise
        if backup.exists():
            shutil.rmtree(backup)
    finally:
        if staged.exists():
            shutil.rmtree(staged, ignore_errors=True)
        if backup.exists() and dest.exists():
            shutil.rmtree(backup, ignore_errors=True)
    return copied


def write_inbox(root: Path, item: dict[str, Any]) -> Path:
    ensure_layout(root)
    name = item["id"].replace(":", "-") + ".json"
    path = root / "inbox" / name
    assert_under_v2(root, path)
    atomic_write_json(path, item)
    return path


def catalog_item(
    *,
    kind: str,
    provider: str,
    slug: str,
    name: str,
    description: str,
    digest: str,
    local_path: str,
    source_type: str,
    dna: dict[str, Any],
    role: str | None,
    frameworks: list[str],
    provenance: dict[str, Any],
    license_obj: dict[str, Any],
    tags: list[str] | None = None,
    categories: list[str] | None = None,
    search_text: str = "",
    anti_slop: list[str] | None = None,
    product_fit: list[str] | None = None,
    extraction_evidence: list[str] | None = None,
    warnings: list[str] | None = None,
    source_id: str | None = None,
    intent: list[str] | None = None,
    modes: list[str] | None = None,
) -> dict[str, Any]:
    item = empty_item_v2()
    item_id = make_id(kind, provider, slug)
    item["id"] = item_id
    item["canonical_id"] = item_id
    item["kind"] = kind
    item["name"] = name
    item["description"] = description
    item["provider"] = provider
    item["role"] = role
    item["dna"] = dna
    item["frameworks"] = frameworks
    item["anti_slop"] = sorted(set(anti_slop or []))
    item["product_fit"] = sorted(set(product_fit if product_fit is not None else (dna.get("product_fit") or [])))
    item["tags"] = tags or []
    item["categories"] = categories or []
    item["intent"] = sorted(set(intent or []))
    item["modes"] = sorted(set(modes or []))
    item["search_text"] = search_text
    item["license"] = license_obj
    item["trust"] = "unknown"
    item["evidence_tier"] = "E0"
    item["execution_class"] = "reference-only"
    item["style_authority"] = "inspiration-only"
    item["untrusted_text"] = True
    item["normalization_status"] = "partial"
    item["selection_policy"] = "full-on-selection" if license_obj.get("status") == "known" else "normalized-card-only"
    if license_obj.get("status") == "known":
        item["execution_class"] = "adapted-candidate"
        item["evidence_tier"] = "E1"
    item["extraction_evidence"] = sorted(set(extraction_evidence or []))
    item["warnings"] = sorted(set(warnings or []))
    item["provenance"] = dict(provenance)
    if source_id:
        item["provenance"]["source_id"] = source_id
    item["source"] = {
        "archive": "",
        "path": local_path,
        "url": None,
        "version": None,
        "content_sha256": digest,
        "provider": provider,
        "type": source_type,
        "retrieval": "offline",
        "local_path": local_path,
        "canonical_url": None,
        "upstream_id": source_id,
    }
    return item

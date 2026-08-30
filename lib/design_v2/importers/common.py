from __future__ import annotations

import hashlib
import os
import re
import shutil
import stat
from pathlib import Path
from typing import Any

from ..bank import DesignV2Error, assert_under_v2, atomic_write_json, ensure_layout, load_policy
from ..dna import extract_query
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
    if extracted.get("aesthetic"):
        dna["aesthetic"] = extracted["aesthetic"]
    if extracted.get("density"):
        dna["density"] = extracted["density"]
    if extracted.get("geometry"):
        dna["geometry"] = extracted["geometry"]
    if extracted.get("motion"):
        dna["motion"] = extracted["motion"]
    if extracted.get("product_fit"):
        dna["product_fit"] = extracted["product_fit"]
    if extracted.get("visual_complexity"):
        dna["visual_complexity"] = extracted["visual_complexity"]
    return dna


def copy_tree_filtered(src: Path, dest: Path, *, skip_suffixes: set[str] | None = None) -> list[str]:
    policy = load_policy()
    skip = {s.lower() for s in (skip_suffixes or set())}
    copied: list[str] = []
    dest.mkdir(parents=True, exist_ok=True)
    for dirpath, dirnames, filenames in os.walk(src, followlinks=False):
        current = Path(dirpath)
        if current.is_symlink():
            raise IngestRejected("symlink")
        rel = current.relative_to(src)
        target_dir = dest / rel if str(rel) != "." else dest
        kept: list[str] = []
        for name in dirnames:
            child = current / name
            if child.is_symlink():
                raise IngestRejected("symlink")
            kept.append(name)
            (target_dir / name).mkdir(parents=True, exist_ok=True)
        dirnames[:] = kept
        for name in filenames:
            if name in {"provenance.json", "ingested.json"}:
                continue
            child = current / name
            st = child.lstat()
            if stat.S_ISLNK(st.st_mode) or not stat.S_ISREG(st.st_mode):
                continue
            suffix = Path(name).suffix.lower()
            if suffix in skip:
                continue
            if not allowed_extension(name, policy) and name.lower() not in {"license", "copying", "design.md"}:
                continue
            out = target_dir / name
            assert_under_v2(dest, out)
            shutil.copyfile(child, out)
            copied.append(str((rel / name) if str(rel) != "." else Path(name)))
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
    item["product_fit"] = list(dna.get("product_fit") or [])
    item["tags"] = tags or []
    item["categories"] = categories or []
    item["search_text"] = search_text
    item["license"] = license_obj
    item["trust"] = "unknown"
    item["evidence_tier"] = "E0"
    item["execution_class"] = "reference-only"
    item["style_authority"] = "inspiration-only"
    item["untrusted_text"] = True
    item["normalization_status"] = "partial"
    item["provenance"] = provenance
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
        "upstream_id": None,
    }
    return item

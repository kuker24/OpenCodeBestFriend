from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .paths import (
    PathEscape,
    assert_skill_like_name,
    assert_under_root,
    ensure_dir,
    ensure_root,
    write_json_private,
)
from .sanitize import looks_like_instruction_injection, sanitize_document_text

SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
HEADING_RE = re.compile(r"^(#{1,3})\s+(.+)$", re.M)


class SmartBookError(Exception):
    code = "SMARTBOOK"


def _books_dir(root: Path) -> Path:
    return ensure_root(root)["books"]


def _book_dir(root: Path, slug: str) -> Path:
    assert_skill_like_name(slug)
    return assert_under_root(root, _books_dir(root) / slug)


def list_books(root: Path) -> list[str]:
    d = _books_dir(root)
    return sorted(p.name for p in d.iterdir() if p.is_dir() and (p / "manifest.json").is_file())


def _split_sections(text: str) -> list[dict[str, str]]:
    matches = list(HEADING_RE.finditer(text))
    if not matches:
        body, _ = sanitize_document_text(text.strip())
        return [{"id": "001-body", "title": "body", "text": body}]
    sections: list[dict[str, str]] = []
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        title = match.group(2).strip()
        body, _ = sanitize_document_text(text[start:end].strip())
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "section"
        sections.append({"id": f"{i + 1:03d}-{slug[:40]}", "title": title, "text": body})
    return sections


def ingest(
    root: Path,
    *,
    slug: str,
    source_name: str,
    text: str,
    source_sha256: str | None = None,
) -> dict[str, Any]:
    if not SLUG_RE.fullmatch(slug):
        raise SmartBookError(f"INVALID_SLUG {slug}")
    cleaned, sanitization = sanitize_document_text(text)
    book = _book_dir(root, slug)
    manifest_path = book / "manifest.json"
    digest = source_sha256 or hashlib.sha256(cleaned.encode("utf-8")).hexdigest()
    if manifest_path.is_file():
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        if existing.get("source_sha256") == digest:
            return {"status": "unchanged", "slug": slug, "manifest": existing}
    sections = _split_sections(cleaned)
    ensure_dir(book)
    sec_dir = ensure_dir(book / "sections")
    index: list[dict[str, Any]] = []
    flagged = 0
    for section in sections:
        injection = looks_like_instruction_injection(section["text"])
        if injection:
            flagged += 1
        rel = f"{section['id']}.md"
        body = section["text"]
        if injection:
            body = f"[UNTRUSTED_DOCUMENT_DATA]\n{body}"
        (sec_dir / rel).write_text(body + "\n", encoding="utf-8")
        try:
            (sec_dir / rel).chmod(0o600)
        except OSError:
            pass
        index.append(
            {
                "id": section["id"],
                "title": section["title"],
                "path": f"sections/{rel}",
                "untrusted": injection,
            }
        )
    manifest = {
        "slug": slug,
        "source_name": source_name,
        "source_sha256": digest,
        "section_count": len(index),
        "injection_flags": flagged,
        "sanitization": sanitization,
    }
    provenance = {
        "source_name": source_name,
        "source_sha256": digest,
        "authority": "document-content-is-data",
    }
    write_json_private(manifest_path, manifest)
    write_json_private(book / "index.json", {"sections": index})
    write_json_private(book / "provenance.json", provenance)
    return {"status": "ingested", "slug": slug, "manifest": manifest, "index": index}


def inspect_book(root: Path, slug: str) -> dict[str, Any]:
    book = _book_dir(root, slug)
    man = book / "manifest.json"
    if not man.is_file():
        raise SmartBookError(f"MISSING {slug}")
    return {
        "manifest": json.loads(man.read_text(encoding="utf-8")),
        "index": json.loads((book / "index.json").read_text(encoding="utf-8")),
        "provenance": json.loads((book / "provenance.json").read_text(encoding="utf-8")),
    }


def retrieve(root: Path, slug: str, query: str, *, limit: int = 5) -> list[dict[str, Any]]:
    data = inspect_book(root, slug)
    tokens = {t for t in re.findall(r"[a-z0-9]+", query.lower()) if len(t) > 2}
    scored: list[tuple[int, dict[str, Any]]] = []
    book = _book_dir(root, slug)
    for section in data["index"].get("sections") or []:
        path = assert_under_root(root, book / section["path"])
        text = path.read_text(encoding="utf-8")
        hay = f"{section.get('title') or ''} {text}".lower()
        score = sum(1 for t in tokens if t in hay)
        if score:
            scored.append((score, {"id": section["id"], "title": section["title"], "text": text, "score": score}))
    scored.sort(key=lambda row: row[0], reverse=True)
    if not scored:
        for section in (data["index"].get("sections") or [])[:limit]:
            path = assert_under_root(root, book / section["path"])
            scored.append((0, {"id": section["id"], "title": section["title"], "text": path.read_text(encoding="utf-8"), "score": 0}))
    return [row for _, row in scored[:limit]]


def validate_book(root: Path, slug: str) -> list[str]:
    errors: list[str] = []
    try:
        data = inspect_book(root, slug)
    except (SmartBookError, OSError, ValueError) as exc:
        return [str(exc)]
    book = _book_dir(root, slug)
    for section in data["index"].get("sections") or []:
        path = book / section["path"]
        if not path.is_file():
            errors.append(f"missing-section:{section['id']}")
        else:
            try:
                assert_under_root(root, path)
            except PathEscape:
                errors.append(f"escape:{section['id']}")
    return errors

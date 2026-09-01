from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any

from .paths import (
    PathEscape,
    atomic_write,
    assert_skill_like_name,
    assert_under_root,
    ensure_dir,
    ensure_root,
    write_json_private,
)
from .sanitize import looks_like_instruction_injection, sanitize_document_text

SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
HEADING_RE = re.compile(r"^(#{1,3})\s+(.+)$", re.M)
CHUNK_CHARS = 1800


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


def _section(i: int, title: str, raw: str, **metadata: Any) -> dict[str, Any]:
    body, _ = sanitize_document_text(raw.strip())
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "section"
    section = {"id": f"{i:03d}-{slug[:40]}", "title": title, "text": body}
    section.update(metadata)
    return section


def _chunk_paragraphs(text: str) -> list[dict[str, Any]]:
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if not paras:
        body, _ = sanitize_document_text(text.strip())
        return [{"id": "001-body", "title": "body", "text": body}]
    chunks: list[str] = []
    buf: list[str] = []
    size = 0
    for para in paras:
        if buf and size + len(para) > CHUNK_CHARS:
            chunks.append("\n\n".join(buf))
            buf = [para]
            size = len(para)
        else:
            buf.append(para)
            size += len(para) + 2
    if buf:
        chunks.append("\n\n".join(buf))
    return [_section(i, f"chunk {i}", chunk) for i, chunk in enumerate(chunks, start=1)]


def _split_sections(text: str) -> list[dict[str, Any]]:
    matches = list(HEADING_RE.finditer(text))
    if matches:
        sections: list[dict[str, Any]] = []
        for i, match in enumerate(matches):
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            title = match.group(2).strip()
            sections.append(_section(i + 1, title, text[start:end]))
        return sections
    pages = [p.strip() for p in text.split("\f") if p.strip()]
    if len(pages) > 1:
        return [_section(i, f"page {i}", page, source_page=i) for i, page in enumerate(pages, start=1)]
    return _chunk_paragraphs(text)


def _sections_from_page_records(page_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = []
    for index, record in enumerate(page_records, start=1):
        source_page = int(record.get("page") or index)
        status = str(record.get("status") or "READY")
        warnings = [str(w) for w in (record.get("warnings") or [])]
        text = str(record.get("text") or "")
        unavailable = not text.strip()
        if unavailable:
            warning_text = ",".join(warnings) or status
            text = f"[SOURCE_PAGE_UNAVAILABLE page={source_page} status={status} warnings={warning_text}]"
        sections.append(
            _section(
                source_page,
                f"page {source_page}",
                text,
                source_page=source_page,
                method=str(record.get("method") or "none"),
                confidence=record.get("confidence"),
                confidence_level=record.get("confidence_level"),
                warnings=warnings,
                source_status=status,
                unavailable=unavailable,
            )
        )
    return sections


def _source_digest(text: str, page_records: list[dict[str, Any]] | None) -> str:
    if page_records:
        canonical = []
        for index, record in enumerate(page_records, start=1):
            cleaned, _ = sanitize_document_text(str(record.get("text") or ""))
            canonical.append(
                {
                    "page": int(record.get("page") or index),
                    "text": cleaned,
                    "status": str(record.get("status") or "READY"),
                    "method": str(record.get("method") or "none"),
                    "confidence": record.get("confidence"),
                    "warnings": [str(w) for w in (record.get("warnings") or [])],
                }
            )
        payload = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    else:
        payload = "\f".join(sanitize_document_text(page)[0] for page in text.split("\f"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def ingest(
    root: Path,
    *,
    slug: str,
    source_name: str,
    text: str,
    source_sha256: str | None = None,
    page_records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if not SLUG_RE.fullmatch(slug):
        raise SmartBookError(f"INVALID_SLUG {slug}")
    cleaned, sanitization = sanitize_document_text(text)
    book = _book_dir(root, slug)
    manifest_path = book / "manifest.json"
    digest = source_sha256 or _source_digest(text, page_records)
    if manifest_path.is_file():
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        if existing.get("source_sha256") == digest:
            return {"status": "unchanged", "slug": slug, "manifest": existing}
    sections = _sections_from_page_records(page_records) if page_records else _split_sections(text)
    books = _books_dir(root)
    stage = Path(tempfile.mkdtemp(prefix=f".{slug}-stage-", dir=str(books)))
    backup = Path(tempfile.mkdtemp(prefix=f".{slug}-backup-", dir=str(books)))
    backup.rmdir()
    sec_dir = ensure_dir(stage / "sections")
    index: list[dict[str, Any]] = []
    flagged = 0
    try:
        for section in sections:
            injection = looks_like_instruction_injection(section["text"])
            if injection:
                flagged += 1
            rel = f"{section['id']}.md"
            body = section["text"]
            if injection:
                body = f"[UNTRUSTED_DOCUMENT_DATA]\n{body}"
            atomic_write(sec_dir / rel, (body + "\n").encode("utf-8"), mode=0o600)
            metadata = {
                key: section[key]
                for key in (
                    "source_page",
                    "method",
                    "confidence",
                    "confidence_level",
                    "warnings",
                    "source_status",
                    "unavailable",
                )
                if key in section
            }
            index.append(
                {
                    "id": section["id"],
                    "title": section["title"],
                    "path": f"sections/{rel}",
                    "untrusted": injection,
                    **metadata,
                }
            )
        manifest = {
            "slug": slug,
            "source_name": source_name,
            "source_sha256": digest,
            "section_count": len(index),
            "injection_flags": flagged,
            "sanitization": sanitization,
            "source_status": (
                "PARTIAL"
                if any(
                    "source_page" in section
                    and (section.get("source_status", "READY") != "READY" or section.get("unavailable"))
                    for section in index
                )
                else "READY"
            ),
            "source_pages": len([section for section in index if "source_page" in section]),
            "source_pages_unavailable": len([section for section in index if section.get("unavailable")]),
        }
        provenance = {
            "source_name": source_name,
            "source_sha256": digest,
            "authority": "document-content-is-data",
            "pages": [
                {
                    key: section[key]
                    for key in (
                        "id",
                        "source_page",
                        "method",
                        "confidence",
                        "confidence_level",
                        "warnings",
                        "source_status",
                        "unavailable",
                    )
                    if key in section
                }
                for section in index
                if "source_page" in section
            ],
        }
        write_json_private(stage / "manifest.json", manifest)
        write_json_private(stage / "index.json", {"sections": index})
        write_json_private(stage / "provenance.json", provenance)

        if book.exists():
            os.replace(book, backup)
        try:
            os.replace(stage, book)
        except Exception:
            if backup.exists() and not book.exists():
                os.replace(backup, book)
            raise
        shutil.rmtree(backup, ignore_errors=True)
        return {"status": "ingested", "slug": slug, "manifest": manifest, "index": index}
    finally:
        shutil.rmtree(stage, ignore_errors=True)
        if book.exists():
            shutil.rmtree(backup, ignore_errors=True)


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


def _retrieve_key(tokens: set[str], title: str, text: str) -> tuple[int, int, int]:
    title_l = (title or "").lower()
    body_l = (text or "").lower()
    title_hits = sum(1 for t in tokens if t in title_l)
    body_hits = sum(1 for t in tokens if t in body_l)
    score = body_hits * 3 + title_hits
    if title_l.rstrip().endswith("?"):
        score -= 2
    return (score, body_hits, len(text))


def retrieve(root: Path, slug: str, query: str, *, limit: int = 5) -> list[dict[str, Any]]:
    data = inspect_book(root, slug)
    tokens = {t for t in re.findall(r"[a-z0-9]+", query.lower()) if len(t) > 2}
    scored: list[tuple[tuple[int, int, int], dict[str, Any]]] = []
    book = _book_dir(root, slug)
    for section in data["index"].get("sections") or []:
        path = assert_under_root(root, book / section["path"])
        text = path.read_text(encoding="utf-8")
        key = _retrieve_key(tokens, str(section.get("title") or ""), text)
        if key[0] > 0 or key[1] > 0:
            scored.append((key, {"id": section["id"], "title": section["title"], "text": text, "score": key[0]}))
    scored.sort(key=lambda row: row[0], reverse=True)
    if not scored:
        for section in (data["index"].get("sections") or [])[:limit]:
            path = assert_under_root(root, book / section["path"])
            scored.append(((0, 0, 0), {"id": section["id"], "title": section["title"], "text": path.read_text(encoding="utf-8"), "score": 0}))
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

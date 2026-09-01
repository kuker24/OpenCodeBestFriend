from __future__ import annotations

import stat
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from .paths import archive_member_ok
from .sanitize import sanitize_document_text

W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
MAX_DOCX_MEMBERS = 4000
MAX_DOCX_MEMBER = 8 * 1024 * 1024
MAX_DOCX_TOTAL = 32 * 1024 * 1024
MAX_DOCX_RATIO = 100.0
MAX_TEXT_BYTES = 8 * 1024 * 1024


class ExtractError(Exception):
    code = "EXTRACT"


def _status(fmt: str, text: str, *, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    cleaned, record = sanitize_document_text(text)
    out: dict[str, Any] = {
        "status": "READY",
        "format": fmt,
        "text": cleaned,
        "sanitization": record,
    }
    if extra:
        out.update(extra)
    return out


def _not_configured(fmt: str, capability: str) -> dict[str, Any]:
    return {"status": "NOT_CONFIGURED", "format": fmt, "text": "", "capability": capability}


def extract_txt(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if len(data) > MAX_TEXT_BYTES:
        raise ExtractError("too_large")
    return _status("txt", data.decode("utf-8", errors="replace"))


def extract_md(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if len(data) > MAX_TEXT_BYTES:
        raise ExtractError("too_large")
    return _status("md", data.decode("utf-8", errors="replace"))


def _reject_hostile_xml(xml: str) -> None:
    lowered = xml.lstrip().lower()
    if "<!doctype" in lowered or "<!entity" in lowered:
        raise ExtractError("xml_dtd")


def _inspect_docx_zip(path: Path) -> None:
    try:
        with zipfile.ZipFile(path) as handle:
            infos = handle.infolist()
    except zipfile.BadZipFile as exc:
        raise ExtractError("bad_zip") from exc
    if len(infos) > MAX_DOCX_MEMBERS:
        raise ExtractError("zip_members")
    total = 0
    for info in infos:
        if info.filename.endswith("/"):
            continue
        if not archive_member_ok(info.filename):
            raise ExtractError("zip_traversal")
        if stat.S_ISLNK(info.external_attr >> 16):
            raise ExtractError("symlink")
        uncompressed = int(info.file_size)
        compressed = max(int(info.compress_size), 1)
        if uncompressed > MAX_DOCX_MEMBER:
            raise ExtractError("zip_member_size")
        if uncompressed / compressed > MAX_DOCX_RATIO:
            raise ExtractError("zip_ratio")
        total += uncompressed
        if total > MAX_DOCX_TOTAL:
            raise ExtractError("zip_total")


def extract_docx(path: Path) -> dict[str, Any]:
    _inspect_docx_zip(path)
    with zipfile.ZipFile(path) as handle:
        try:
            xml = handle.read("word/document.xml").decode("utf-8", errors="replace")
        except KeyError as exc:
            raise ExtractError("missing_document_xml") from exc
    _reject_hostile_xml(xml)
    root = ET.fromstring(xml)
    body = root.find(f"{W_NS}body")
    if body is None:
        body = root
    paragraphs: list[str] = []
    tables: list[list[list[str]]] = []

    def para_text(node: ET.Element) -> str:
        return "".join((t.text or "") for t in node.iter(f"{W_NS}t")).strip()

    for child in list(body):
        if child.tag == f"{W_NS}p":
            line = para_text(child)
            if line:
                paragraphs.append(line)
        elif child.tag == f"{W_NS}tbl":
            rows: list[list[str]] = []
            for tr in child.iter(f"{W_NS}tr"):
                cells = [para_text(tc) for tc in tr.findall(f"{W_NS}tc")]
                if cells:
                    rows.append(cells)
            if rows:
                tables.append(rows)
    text = "\n".join(paragraphs)
    return _status("docx", text, extra={"tables": tables})


def extract_pdf(path: Path) -> dict[str, Any]:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception:
        return _not_configured("pdf", "PDF_READ")
    try:
        reader = PdfReader(str(path))
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
    except Exception as exc:
        raise ExtractError("pdf_failed") from exc
    return _status("pdf", "\n".join(pages), extra={"pages": len(pages)})


def extract_image(path: Path) -> dict[str, Any]:
    try:
        from PIL import Image  # type: ignore
    except Exception:
        return _not_configured(path.suffix.lstrip(".").lower() or "image", "IMAGE_READ")
    try:
        with Image.open(path) as img:
            info = {"width": img.width, "height": img.height, "mode": img.mode}
    except Exception as exc:
        raise ExtractError("image_failed") from exc
    return {
        "status": "READY",
        "format": path.suffix.lstrip(".").lower() or "image",
        "text": "",
        "image": info,
        "note": "image has no native text layer",
    }


def extract_file(path: Path) -> dict[str, Any]:
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        raise ExtractError("missing")
    suffix = resolved.suffix.lower()
    if suffix in {".txt"}:
        return extract_txt(resolved)
    if suffix in {".md", ".markdown"}:
        return extract_md(resolved)
    if suffix == ".docx":
        return extract_docx(resolved)
    if suffix == ".pdf":
        return extract_pdf(resolved)
    if suffix in {".png", ".jpg", ".jpeg", ".webp"}:
        return extract_image(resolved)
    raise ExtractError(f"unsupported:{suffix or 'none'}")

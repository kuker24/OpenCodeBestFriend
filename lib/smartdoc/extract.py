from __future__ import annotations

import shutil
import stat
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from . import ocr as ocr_mod
from .paths import archive_member_ok
from .preprocess import PreprocessError, prepare_working_image
from .sanitize import sanitize_document_text

W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
MAX_DOCX_MEMBERS = 4000
MAX_DOCX_MEMBER = 8 * 1024 * 1024
MAX_DOCX_TOTAL = 32 * 1024 * 1024
MAX_DOCX_RATIO = 100.0
MAX_TEXT_BYTES = 8 * 1024 * 1024
MIN_NATIVE_CHARS = 40
MIN_PRINTABLE_RATIO = 0.85
OCR_DPI = 200
OCR_POLICIES = frozenset({"AUTO", "NEVER", "ALWAYS"})
RASTER_TIMEOUT_SEC = 30


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


def normalize_ocr_policy(value: str | None) -> str:
    raw = str(value or "AUTO").strip().upper()
    return raw if raw in OCR_POLICIES else "AUTO"


def native_text_sufficient(text: str) -> bool:
    if not text:
        return False
    non_ws = [c for c in text if not c.isspace()]
    if len(non_ws) < MIN_NATIVE_CHARS:
        return False
    printable = sum(1 for c in non_ws if c.isprintable())
    return (printable / len(non_ws)) >= MIN_PRINTABLE_RATIO


def _merge_sanitization(records: list[dict[str, int]]) -> dict[str, int]:
    out = {"zero_width": 0, "unicode_tags": 0, "controls": 0}
    for rec in records:
        for key in out:
            out[key] += int(rec.get(key) or 0)
    return out


def _resolve_ocr_langs(languages: list[str] | None, contract_language: str | None = None) -> list[str]:
    return ocr_mod.select_languages(
        ocr_mod.list_languages(),
        requested=languages,
        contract_language=contract_language,
    )


def raster_pdf_page(pdf: Path, page: int, dest_dir: Path, *, dpi: int = OCR_DPI) -> Path:
    binary = shutil.which("pdftoppm")
    if not binary:
        raise FileNotFoundError("PDF_RASTER_NOT_CONFIGURED")
    dest_dir.mkdir(parents=True, exist_ok=True)
    prefix = dest_dir / f"page-{page}"
    cmd = [
        binary,
        "-f",
        str(page),
        "-l",
        str(page),
        "-png",
        "-r",
        str(min(dpi, 200)),
        "-singlefile",
        str(pdf),
        str(prefix),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=RASTER_TIMEOUT_SEC, check=False)
    except subprocess.TimeoutExpired as exc:
        raise FileNotFoundError("PDF_RASTER_FAILED") from exc
    out = dest_dir / f"page-{page}.png"
    if not out.is_file():
        alt = dest_dir / f"page-{page}-1.png"
        if alt.is_file():
            return alt
        if proc.returncode != 0:
            raise FileNotFoundError("PDF_RASTER_FAILED")
        raise FileNotFoundError("end")
    return out


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


def _page_record(
    page: int,
    *,
    method: str,
    text: str,
    confidence: float | None = None,
    confidence_level: str | None = None,
    engine: str | None = None,
    language: str | None = None,
    warnings: list[str] | None = None,
    status: str = "READY",
) -> dict[str, Any]:
    return {
        "page": page,
        "method": method,
        "text": text,
        "confidence": confidence,
        "confidence_level": confidence_level,
        "engine": engine,
        "language": language,
        "warnings": list(warnings or []),
        "status": status,
    }


def _ocr_page_image(image: Path, languages: list[str]) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="ocbf-ocr-work-") as raw:
        work = Path(raw) / "work.png"
        try:
            prepare_working_image(image, work)
            target = work
        except PreprocessError as exc:
            if exc.code in {"IMAGE_TOO_LARGE", "IMAGE_DECOMPRESSION_RISK", "IMAGE_FAILED"}:
                return {
                    "status": exc.code,
                    "text": "",
                    "warnings": [exc.code],
                    "tokens": [],
                    "confidence": None,
                }
            target = image
        return ocr_mod.ocr_image(target, languages=languages, timeout=ocr_mod.OCR_TIMEOUT_PAGE_SEC)


def extract_pdf(
    path: Path,
    *,
    ocr: str = "AUTO",
    languages: list[str] | None = None,
    contract_language: str | None = None,
) -> dict[str, Any]:
    policy = normalize_ocr_policy(ocr)
    native_pages: list[str] | None = None
    try:
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(str(path))
        native_pages = [(page.extract_text() or "") for page in reader.pages]
    except ExtractError:
        raise
    except Exception:
        native_pages = None

    ocr_langs = _resolve_ocr_langs(languages, contract_language)
    can_ocr = bool(ocr_mod.tesseract_bin() and ocr_langs and shutil.which("pdftoppm"))
    records: list[dict[str, Any]] = []
    sanitizers: list[dict[str, int]] = []
    failed: list[int] = []

    if native_pages is not None:
        page_count = len(native_pages)
        if page_count > ocr_mod.MAX_OCR_PAGES:
            page_count = ocr_mod.MAX_OCR_PAGES
        for idx in range(page_count):
            raw_native = native_pages[idx]
            cleaned_native, rec = sanitize_document_text(raw_native)
            page_no = idx + 1
            use_native = policy != "ALWAYS" and native_text_sufficient(cleaned_native)
            if policy == "NEVER" or use_native:
                if native_text_sufficient(cleaned_native) or policy == "NEVER":
                    records.append(
                        _page_record(
                            page_no,
                            method="native_text" if cleaned_native.strip() else "none",
                            text=cleaned_native if native_text_sufficient(cleaned_native) or policy == "NEVER" else "",
                        )
                    )
                    sanitizers.append(rec)
                    if policy == "NEVER" and not native_text_sufficient(cleaned_native):
                        records[-1]["warnings"] = ["OCR_NEVER"]
                        records[-1]["method"] = "none"
                    continue
            if policy == "NEVER":
                records.append(_page_record(page_no, method="none", text="", warnings=["OCR_NEVER"]))
                continue
            if not can_ocr:
                cap = "OCR_PDF" if ocr_mod.tesseract_bin() else "OCR_ENGINE"
                if not shutil.which("pdftoppm"):
                    cap = "PDF_RASTER_NOT_CONFIGURED"
                if not records and page_count == 1:
                    return _not_configured("pdf", cap)
                records.append(_page_record(page_no, method="none", text="", status="NOT_CONFIGURED", warnings=[cap]))
                failed.append(page_no)
                continue
            with tempfile.TemporaryDirectory(prefix="ocbf-raster-") as raw:
                dest = Path(raw)
                try:
                    raster = raster_pdf_page(path, page_no, dest)
                    ocr_res = _ocr_page_image(raster, ocr_langs)
                except FileNotFoundError:
                    records.append(
                        _page_record(
                            page_no,
                            method="none",
                            text="",
                            status="PDF_RASTER_FAILED",
                            warnings=["PDF_RASTER_FAILED"],
                        )
                    )
                    failed.append(page_no)
                    continue
            if ocr_res.get("status") == "READY":
                records.append(
                    _page_record(
                        page_no,
                        method="ocr",
                        text=ocr_res.get("text") or "",
                        confidence=ocr_res.get("confidence"),
                        confidence_level=ocr_res.get("confidence_level"),
                        engine=ocr_res.get("engine") or "tesseract",
                        language=ocr_res.get("language"),
                        warnings=ocr_res.get("warnings") or [],
                    )
                )
                sanitizers.append(ocr_res.get("sanitization") or {"zero_width": 0, "unicode_tags": 0, "controls": 0})
            else:
                records.append(
                    _page_record(
                        page_no,
                        method="none",
                        text="",
                        status=str(ocr_res.get("status") or "OCR_FAILED"),
                        warnings=ocr_res.get("warnings") or [str(ocr_res.get("status"))],
                    )
                )
                failed.append(page_no)
        return _pdf_result(records, sanitizers, failed, native_missing=False)

    if policy == "NEVER":
        return _not_configured("pdf", "PDF_READ")
    if not ocr_mod.tesseract_bin() or not ocr_langs:
        return _not_configured("pdf", "OCR_PDF" if shutil.which("pdftoppm") else "OCR_ENGINE")
    if not shutil.which("pdftoppm"):
        return _not_configured("pdf", "PDF_RASTER_NOT_CONFIGURED")

    with tempfile.TemporaryDirectory(prefix="ocbf-raster-") as raw:
        dest = Path(raw)
        for page_no in range(1, ocr_mod.MAX_OCR_PAGES + 1):
            try:
                raster = raster_pdf_page(path, page_no, dest)
            except FileNotFoundError:
                break
            ocr_res = _ocr_page_image(raster, ocr_langs)
            try:
                raster.unlink(missing_ok=True)
            except OSError:
                pass
            if ocr_res.get("status") == "READY":
                records.append(
                    _page_record(
                        page_no,
                        method="ocr",
                        text=ocr_res.get("text") or "",
                        confidence=ocr_res.get("confidence"),
                        confidence_level=ocr_res.get("confidence_level"),
                        engine=ocr_res.get("engine") or "tesseract",
                        language=ocr_res.get("language"),
                        warnings=ocr_res.get("warnings") or [],
                    )
                )
                sanitizers.append(ocr_res.get("sanitization") or {"zero_width": 0, "unicode_tags": 0, "controls": 0})
            else:
                records.append(
                    _page_record(
                        page_no,
                        method="none",
                        text="",
                        status=str(ocr_res.get("status") or "OCR_FAILED"),
                        warnings=ocr_res.get("warnings") or [],
                    )
                )
                failed.append(page_no)
    if not records:
        return _not_configured("pdf", "OCR_PDF")
    return _pdf_result(records, sanitizers, failed, native_missing=True)


def _pdf_result(
    records: list[dict[str, Any]],
    sanitizers: list[dict[str, int]],
    failed: list[int],
    *,
    native_missing: bool,
) -> dict[str, Any]:
    texts = [r.get("text") or "" for r in records]
    ready = sum(1 for r in records if r.get("status") == "READY" and r.get("method") != "none")
    none_only = all(r.get("method") == "none" for r in records) if records else True
    if none_only and failed:
        cap = "PDF_RASTER_NOT_CONFIGURED"
        for rec in records:
            for warn in rec.get("warnings") or []:
                cap = str(warn)
                break
        return {
            "status": "NOT_CONFIGURED",
            "format": "pdf",
            "text": "",
            "capability": cap,
            "pages": len(records),
            "page_records": records,
            "pages_failed": failed,
        }
    if none_only and not any((r.get("text") or "").strip() for r in records):
        cap = "PDF_READ" if native_missing else "PDF_RASTER_NOT_CONFIGURED"
        return {
            "status": "NOT_CONFIGURED",
            "format": "pdf",
            "text": "",
            "capability": cap,
            "pages": len(records),
            "page_records": records,
        }
    status = "PARTIAL" if failed and ready else "READY"
    if failed and not ready:
        status = "NOT_CONFIGURED"
    return {
        "status": status,
        "format": "pdf",
        "text": "\f".join(texts),
        "pages": len(records),
        "page_records": records,
        "pages_ready": ready,
        "pages_failed": failed,
        "sanitization": _merge_sanitization(sanitizers),
    }


def extract_image(
    path: Path,
    *,
    ocr: str = "AUTO",
    languages: list[str] | None = None,
    contract_language: str | None = None,
) -> dict[str, Any]:
    fmt = path.suffix.lstrip(".").lower() or "image"
    policy = normalize_ocr_policy(ocr)
    try:
        from PIL import Image  # type: ignore
    except Exception:
        return _not_configured(fmt, "IMAGE_READ")
    try:
        with Image.open(path) as img:
            img.load()
            info = {"width": img.width, "height": img.height, "mode": img.mode}
            pixels = img.width * img.height
    except Exception as exc:
        name = type(exc).__name__
        if "DecompressionBomb" in name:
            raise ExtractError("IMAGE_DECOMPRESSION_RISK") from exc
        raise ExtractError("image_failed") from exc
    from .preprocess import MAX_IMAGE_PIXELS

    if pixels > MAX_IMAGE_PIXELS:
        raise ExtractError("IMAGE_TOO_LARGE")
    base: dict[str, Any] = {
        "format": fmt,
        "image": info,
        "pages": 1,
    }
    if policy == "NEVER":
        return {
            "status": "READY",
            "text": "",
            "note": "image has no native text layer",
            "page_records": [_page_record(1, method="none", text="", warnings=["OCR_NEVER"])],
            **base,
        }
    ocr_langs = _resolve_ocr_langs(languages, contract_language)
    if not ocr_mod.tesseract_bin() or not ocr_langs:
        cap = "OCR_LANGUAGE_NOT_CONFIGURED" if ocr_mod.tesseract_bin() else "OCR_IMAGE"
        return {
            "status": "NOT_CONFIGURED",
            "text": "",
            "capability": cap,
            "page_records": [_page_record(1, method="none", text="", status="NOT_CONFIGURED", warnings=[cap])],
            **base,
        }
    ocr_res = _ocr_page_image(path, ocr_langs)
    if ocr_res.get("status") != "READY":
        return {
            "status": ocr_res.get("status") or "OCR_FAILED",
            "text": "",
            "capability": ocr_res.get("capability") or ocr_res.get("status"),
            "page_records": [
                _page_record(
                    1,
                    method="none",
                    text="",
                    status=str(ocr_res.get("status") or "OCR_FAILED"),
                    warnings=ocr_res.get("warnings") or [],
                )
            ],
            **base,
        }
    record = _page_record(
        1,
        method="ocr",
        text=ocr_res.get("text") or "",
        confidence=ocr_res.get("confidence"),
        confidence_level=ocr_res.get("confidence_level"),
        engine=ocr_res.get("engine") or "tesseract",
        language=ocr_res.get("language"),
        warnings=ocr_res.get("warnings") or [],
    )
    return {
        "status": "READY",
        "text": record["text"],
        "page_records": [record],
        "sanitization": ocr_res.get("sanitization"),
        **base,
    }


def extract_file(
    path: Path,
    *,
    ocr: str = "AUTO",
    languages: list[str] | None = None,
    contract_language: str | None = None,
) -> dict[str, Any]:
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
        return extract_pdf(resolved, ocr=ocr, languages=languages, contract_language=contract_language)
    if suffix in {".png", ".jpg", ".jpeg", ".webp"}:
        return extract_image(resolved, ocr=ocr, languages=languages, contract_language=contract_language)
    raise ExtractError(f"unsupported:{suffix or 'none'}")

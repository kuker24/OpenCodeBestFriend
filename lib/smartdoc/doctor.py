from __future__ import annotations

import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any

from .capabilities import capability_matrix
from .extract import extract_file
from .ocr import list_languages, tesseract_bin
from .paths import resolve_smartdoc_root
from .profiles import create_profile, delete_profile, load_profile
from .render import assemble_pdf, render_page_images
from .smartbook import ingest, retrieve, validate_book

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _check(name: str, status: str, **extra: Any) -> dict[str, Any]:
    row = {"name": name, "status": status}
    row.update(extra)
    return row


def _tiny_docx(path: Path) -> None:
    document = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<w:document xmlns:w="{W}"><w:body>'
        "<w:p><w:r><w:t>doctor probe</w:t></w:r></w:p>"
        "</w:body></w:document>"
    )
    with zipfile.ZipFile(path, "w") as handle:
        handle.writestr("word/document.xml", document)
        handle.writestr("[Content_Types].xml", "<Types></Types>")


def run_doctor(*, root: Path | None = None) -> dict[str, Any]:
    resolved = root or resolve_smartdoc_root()
    matrix = capability_matrix()
    checks: list[dict[str, Any]] = []
    probe = Path(tempfile.mkdtemp(prefix="ocbf-smartdoc-doctor-"))
    try:
        parent = resolved.parent if resolved.parent != resolved else resolved
        writable = os.access(str(resolved), os.W_OK) if resolved.exists() else os.access(str(parent), os.W_OK)
        checks.append(_check("root_writable", "PASS" if writable else "FAIL", path=str(resolved)))

        try:
            created = create_profile(probe, "doctor-probe", [{"label": "id", "value": "x"}])
            loaded = load_profile(probe, "doctor-probe")
            delete_profile(probe, "doctor-probe")
            gone = not (probe / "profiles" / "doctor-probe.json").is_file()
            ok = created.get("profileName") == "doctor-probe" and loaded.get("profileName") == "doctor-probe" and gone
            checks.append(_check("profile_roundtrip", "PASS" if ok else "FAIL"))
        except Exception as exc:
            checks.append(_check("profile_roundtrip", "FAIL", detail=str(exc)))

        docx = probe / "probe.docx"
        _tiny_docx(docx)
        try:
            extracted = extract_file(docx)
            ok = extracted.get("status") == "READY" and "doctor probe" in (extracted.get("text") or "")
            checks.append(_check("docx_extraction", "PASS" if ok else "FAIL"))
        except Exception as exc:
            checks.append(_check("docx_extraction", "FAIL", detail=str(exc)))

        if matrix["PDF_READ"] == "READY":
            checks.append(_check("pypdf_import", "PASS", dependency="pypdf"))
        else:
            checks.append(_check("pypdf_import", "NOT_CONFIGURED", dependency="pypdf", partial=False))

        try:
            pages = render_page_images("doctor probe line")
            checks.append(_check("pillow_render", "PASS" if pages else "FAIL"))
            pdf_path = probe / "probe.pdf"
            assemble_pdf(pages, pdf_path)
            checks.append(_check("pdf_assembly", "PASS" if pdf_path.is_file() else "FAIL"))
        except Exception as exc:
            status = "NOT_CONFIGURED" if matrix["HANDWRITING"] != "READY" else "FAIL"
            checks.append(_check("pillow_render", status, detail=str(exc)))
            checks.append(_check("pdf_assembly", status, detail=str(exc)))

        raster_cap = matrix["POST_PDF_RASTER_QA"]
        checks.append(
            _check(
                "pdftoppm_post_raster",
                "PASS" if raster_cap == "READY" else raster_cap,
                dependency="pdftoppm",
            )
        )

        tess = tesseract_bin()
        if tess:
            checks.append(_check("tesseract", "PASS", dependency="tesseract", path=tess))
            langs = list_languages(force=True)
            if langs:
                checks.append(_check("ocr_languages", "PASS", languages=langs))
            else:
                checks.append(_check("ocr_languages", "NOT_CONFIGURED", reason="OCR_LANGUAGE_NOT_CONFIGURED"))
        else:
            checks.append(_check("tesseract", "NOT_CONFIGURED", dependency="tesseract"))
            checks.append(_check("ocr_languages", "NOT_CONFIGURED"))

        if matrix.get("OCR_IMAGE") == "READY":
            try:
                from PIL import Image, ImageDraw  # type: ignore

                img_path = probe / "ocr-probe.png"
                img = Image.new("RGB", (80, 24), "white")
                ImageDraw.Draw(img).text((2, 2), "Hi", fill="black")
                img.save(img_path)
                extracted = extract_file(img_path, ocr="AUTO")
                ok = extracted.get("status") in {"READY", "PARTIAL"} and extracted.get("page_records")
                checks.append(_check("ocr_image", "PASS" if ok else "FAIL"))
            except Exception as exc:
                checks.append(_check("ocr_image", "FAIL", detail=str(exc)))
        else:
            checks.append(_check("ocr_image", "NOT_CONFIGURED"))

        if matrix.get("OCR_PDF") == "READY":
            try:
                from PIL import Image  # type: ignore

                pdf_path = probe / "ocr-probe.pdf"
                Image.new("RGB", (80, 24), "white").save(pdf_path, "PDF")
                extracted = extract_file(pdf_path, ocr="AUTO")
                status = extracted.get("status")
                if status in {"READY", "PARTIAL"}:
                    checks.append(_check("ocr_pdf", "PASS"))
                elif status == "NOT_CONFIGURED":
                    checks.append(_check("ocr_pdf", "NOT_CONFIGURED", capability=extracted.get("capability")))
                else:
                    checks.append(_check("ocr_pdf", "FAIL", detail=str(status)))
            except Exception as exc:
                checks.append(_check("ocr_pdf", "FAIL", detail=str(exc)))
        else:
            checks.append(_check("ocr_pdf", "NOT_CONFIGURED"))

        if matrix.get("PDF_READ") == "READY" and matrix.get("OCR_PDF") == "READY":
            checks.append(_check("mixed_document", "PASS", detail="hybrid native/OCR path available"))
        elif matrix.get("OCR_PDF") == "READY" or matrix.get("PDF_READ") == "READY":
            checks.append(_check("mixed_document", "NOT_CONFIGURED", partial=True))
        else:
            checks.append(_check("mixed_document", "NOT_CONFIGURED"))

        try:
            book = ingest(probe, slug="doctor-book", source_name="probe.txt", text="# Probe\ndoctor fact.\n")
            hits = retrieve(probe, "doctor-book", "doctor fact")
            errors = validate_book(probe, "doctor-book")
            ok = book.get("status") == "ingested" and bool(hits) and not errors
            checks.append(_check("smartbook_read_write", "PASS" if ok else "FAIL"))
        except Exception as exc:
            checks.append(_check("smartbook_read_write", "FAIL", detail=str(exc)))
    finally:
        leftover = probe.exists()
        shutil.rmtree(probe, ignore_errors=True)
        checks.append(_check("temp_cleanup", "PASS" if leftover and not probe.exists() else "FAIL", path=str(probe)))

    failed = any(c["status"] == "FAIL" for c in checks)
    return {"root": str(resolved), "ok": not failed, "capabilities": matrix, "checks": checks}

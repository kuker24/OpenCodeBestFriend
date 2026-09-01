from __future__ import annotations

import shutil
from typing import Any

from .ocr import list_languages, tesseract_bin


def _optional_mod(name: str) -> bool:
    try:
        __import__(name)
        return True
    except Exception:
        return False


def capability_matrix() -> dict[str, str]:
    pillow = _optional_mod("PIL")
    pypdf = _optional_mod("pypdf")
    pdftoppm = bool(shutil.which("pdftoppm"))
    tess = bool(tesseract_bin())
    langs = list_languages() if tess else []
    ocr_engine = "READY" if tess else "NOT_CONFIGURED"
    ocr_image = "READY" if tess and pillow and langs else "NOT_CONFIGURED"
    ocr_pdf = "READY" if ocr_image == "READY" and pdftoppm else "NOT_CONFIGURED"
    ocr = "READY" if ocr_image == "READY" or ocr_pdf == "READY" else "NOT_CONFIGURED"
    return {
        "TXT_WRITE": "READY",
        "MARKDOWN_WRITE": "READY",
        "DOCX_READ": "READY",
        "PDF_READ": "READY" if pypdf else "NOT_CONFIGURED",
        "IMAGE_READ": "READY" if pillow else "NOT_CONFIGURED",
        "PDF_RENDER": "READY" if pillow else "NOT_CONFIGURED",
        "HANDWRITING": "READY" if pillow else "NOT_CONFIGURED",
        "OCR": ocr,
        "OCR_ENGINE": ocr_engine,
        "OCR_IMAGE": ocr_image,
        "OCR_PDF": ocr_pdf,
        "POST_PDF_RASTER_QA": "READY" if pdftoppm else "NOT_CONFIGURED",
    }


def as_rows(matrix: dict[str, str] | None = None) -> list[tuple[str, str]]:
    data = matrix or capability_matrix()
    return [(k, data[k]) for k in data]


def status_payload(root: str | None = None) -> dict[str, Any]:
    matrix = capability_matrix()
    langs = list_languages() if matrix.get("OCR_ENGINE") == "READY" else []
    return {"root": root, "capabilities": matrix, "ocr_languages": langs}

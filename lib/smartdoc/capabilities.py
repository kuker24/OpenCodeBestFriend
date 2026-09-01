from __future__ import annotations

import shutil
from typing import Any


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
    return {
        "TXT_WRITE": "READY",
        "MARKDOWN_WRITE": "READY",
        "DOCX_READ": "READY",
        "PDF_READ": "READY" if pypdf else "NOT_CONFIGURED",
        "IMAGE_READ": "READY" if pillow else "NOT_CONFIGURED",
        "PDF_RENDER": "READY" if pillow else "NOT_CONFIGURED",
        "HANDWRITING": "READY" if pillow else "NOT_CONFIGURED",
        "OCR": "NOT_CONFIGURED",
        "POST_PDF_RASTER_QA": "READY" if pdftoppm else "NOT_CONFIGURED",
    }


def as_rows(matrix: dict[str, str] | None = None) -> list[tuple[str, str]]:
    data = matrix or capability_matrix()
    return [(k, data[k]) for k in data]


def status_payload(root: str | None = None) -> dict[str, Any]:
    return {"root": root, "capabilities": capability_matrix()}

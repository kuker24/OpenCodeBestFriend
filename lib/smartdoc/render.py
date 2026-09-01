from __future__ import annotations

import hashlib
import io
import math
import tempfile
import textwrap
from pathlib import Path
from typing import Any

from .capabilities import capability_matrix
from .contract import ContractError, assert_content_unchanged
from .paths import atomic_write, resolve_output_path, safe_filename
from .styles import DEFAULT_STYLE


class RenderError(Exception):
    code = "RENDER"


def _require_pillow():
    try:
        from PIL import Image, ImageDraw, ImageFont  # type: ignore
    except Exception as exc:
        raise RenderError("HANDWRITING_NOT_CONFIGURED") from exc
    return Image, ImageDraw, ImageFont


def _seed_int(seed: int, page: int, index: int) -> float:
    raw = hashlib.sha256(f"{seed}:{page}:{index}".encode("utf-8")).digest()
    return int.from_bytes(raw[:4], "big") / 0xFFFFFFFF


def _jitter(seed: int, page: int, index: int, amplitude: float) -> float:
    return (_seed_int(seed, page, index) * 2.0 - 1.0) * amplitude


def wrap_lines(content: str, width: int = 72) -> list[str]:
    lines: list[str] = []
    for para in content.splitlines() or [""]:
        if not para.strip():
            lines.append("")
            continue
        lines.extend(textwrap.wrap(para, width=width) or [""])
    return lines


def render_page_images(
    content: str,
    *,
    style: dict[str, Any] | None = None,
    identity_lines: list[str] | None = None,
    seed: int = 1,
) -> list[bytes]:
    Image, ImageDraw, ImageFont = _require_pillow()
    cfg = dict(DEFAULT_STYLE)
    if style:
        cfg.update(style)
    width, height = 1240, 1754
    line_gap = int(cfg.get("lineGap") or 28)
    font_size = int(cfg.get("fontSize") or 20)
    left = int(cfg.get("leftMargin") or 92)
    baseline_j = float(cfg.get("baselineJitter") or 1.5)
    rot_j = float(cfg.get("rotationJitter") or 1.1)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()
    header = list(identity_lines or [])
    body = wrap_lines(content, width=70)
    lines = header + ([""] if header else []) + body
    usable = height - 120
    per_page = max(1, usable // line_gap)
    pages: list[bytes] = []
    for page_i in range(0, max(1, math.ceil(len(lines) / per_page))):
        chunk = lines[page_i * per_page : (page_i + 1) * per_page]
        img = Image.new("RGB", (width, height), cfg.get("paperTone") or "#fbfaf4")
        draw = ImageDraw.Draw(img)
        for y in range(80, height - 40, line_gap):
            draw.line([(left - 20, y), (width - 40, y)], fill=cfg.get("line") or "#9db8e0", width=1)
        draw.line([(left - 30, 40), (left - 30, height - 30)], fill=cfg.get("margin") or "#d94a4a", width=2)
        y = 80
        for idx, line in enumerate(chunk):
            dx = _jitter(seed, page_i, idx, 1.5)
            dy = _jitter(seed, page_i, idx + 17, baseline_j)
            draw.text((left + dx, y + dy), line, fill=cfg.get("ink") or "#1e3a8a", font=font)
            y += line_gap
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        pages.append(buf.getvalue())
    return pages


def assemble_pdf(pages: list[bytes], dest: Path) -> Path:
    Image, _Draw, _Font = _require_pillow()
    images = [Image.open(io.BytesIO(p)).convert("RGB") for p in pages]
    if not images:
        raise RenderError("no pages")
    first, rest = images[0], images[1:]
    buf = io.BytesIO()
    try:
        first.save(buf, save_all=True, append_images=rest, format="PDF")
        atomic_write(dest, buf.getvalue(), mode=0o600)
    finally:
        for img in images:
            img.close()
    return dest


def verify_rendered_pdf(path: Path, expected_pages: int, matrix: dict[str, str]) -> dict[str, Any]:
    warnings: list[str] = []
    structural = "NOT_CONFIGURED"
    if matrix.get("PDF_READ") == "READY":
        try:
            from pypdf import PdfReader  # type: ignore

            structural = "PASS" if len(PdfReader(str(path)).pages) == expected_pages else "FAIL"
        except Exception:
            structural = "FAIL"
        if structural == "FAIL":
            warnings.append("STRUCTURAL_QA_FAILED")

    raster = "NOT_CONFIGURED"
    if matrix.get("POST_PDF_RASTER_QA") == "READY":
        try:
            from .extract import raster_pdf_page

            with tempfile.TemporaryDirectory(prefix="ocbf-render-qa-") as raw:
                work = Path(raw)
                first = raster_pdf_page(path, 1, work)
                last = first if expected_pages == 1 else raster_pdf_page(path, expected_pages, work)
                raster = "PASS" if first.stat().st_size > 0 and last.stat().st_size > 0 else "FAIL"
        except Exception:
            raster = "FAIL"
        if raster == "FAIL":
            warnings.append("POST_PDF_RASTER_QA_FAILED")
    return {"structural_qa": structural, "post_pdf_raster_qa": raster, "warnings": warnings}


def render_handwriting(
    content: str,
    dest_dir: Path,
    filename: str,
    *,
    contract: dict[str, Any] | None = None,
    style: dict[str, Any] | None = None,
    identity_lines: list[str] | None = None,
    seed: int = 1,
    overwrite: bool = False,
) -> dict[str, Any]:
    matrix = capability_matrix()
    if matrix["HANDWRITING"] != "READY":
        return {"status": "NOT_CONFIGURED", "capability": "HANDWRITING"}
    if contract is not None:
        try:
            assert_content_unchanged(contract, content)
        except ContractError as exc:
            raise RenderError(str(exc)) from exc
    pages = render_page_images(content, style=style, identity_lines=identity_lines, seed=seed)
    preview_dir = dest_dir / "previews"
    preview_dir.mkdir(parents=True, exist_ok=True)
    preview_paths: list[str] = []
    for i, blob in enumerate(pages, start=1):
        preview = preview_dir / f"page-{i:03d}.png"
        atomic_write(preview, blob, mode=0o600)
        preview_paths.append(str(preview))
    pdf_path = resolve_output_path(dest_dir, safe_filename(filename), overwrite=overwrite)
    assemble_pdf(pages, pdf_path)
    verification = verify_rendered_pdf(pdf_path, len(pages), matrix)
    return {
        "status": "PARTIAL" if verification["warnings"] else "READY",
        "pdf": str(pdf_path),
        "previews": preview_paths,
        "pages": len(pages),
        **verification,
    }

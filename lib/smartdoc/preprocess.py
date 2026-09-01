from __future__ import annotations

from pathlib import Path
from typing import Any

MAX_IMAGE_PIXELS = 40_000_000
MAX_RASTER_EDGE = 3300
UPSCALE_MIN_EDGE = 40
UPSCALE_TARGET = 160
MAX_UPSCALE = 8.0


class PreprocessError(Exception):
    def __init__(self, code: str, detail: str = ""):
        self.code = code
        super().__init__(detail or code)


def prepare_working_image(src: Path, dest: Path) -> dict[str, Any]:
    try:
        from PIL import Image, ImageOps  # type: ignore
    except Exception as exc:
        raise PreprocessError("IMAGE_READ") from exc
    try:
        with Image.open(src) as im:
            im.load()
            src_w, src_h = im.size
            if src_w * src_h > MAX_IMAGE_PIXELS:
                raise PreprocessError("IMAGE_TOO_LARGE")
            work = ImageOps.exif_transpose(im)
            if work is None:
                work = im
            work = work.convert("RGB")
            work = ImageOps.grayscale(work)
            work = ImageOps.autocontrast(work)
            bw, bh = work.size
            longest = max(bw, bh) or 1
            resample = getattr(getattr(Image, "Resampling", Image), "LANCZOS", 1)
            if longest < UPSCALE_MIN_EDGE:
                scale = min(UPSCALE_TARGET / longest, MAX_UPSCALE)
                work = work.resize((max(1, int(bw * scale)), max(1, int(bh * scale))), resample)
                bw, bh = work.size
                longest = max(bw, bh)
            if longest > MAX_RASTER_EDGE:
                scale = MAX_RASTER_EDGE / longest
                work = work.resize((max(1, int(bw * scale)), max(1, int(bh * scale))), resample)
            dest.parent.mkdir(parents=True, exist_ok=True)
            work.save(dest)
            return {
                "width": work.size[0],
                "height": work.size[1],
                "src_width": src_w,
                "src_height": src_h,
                "mode": work.mode,
            }
    except PreprocessError:
        raise
    except Exception as exc:
        name = type(exc).__name__
        if "DecompressionBomb" in name:
            raise PreprocessError("IMAGE_DECOMPRESSION_RISK") from exc
        raise PreprocessError("IMAGE_FAILED") from exc

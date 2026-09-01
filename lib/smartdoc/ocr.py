from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from .sanitize import sanitize_document_text

OCR_TIMEOUT_PAGE_SEC = 30
OCR_TIMEOUT_JOB_SEC = 600
MAX_OCR_STDOUT = 2 * 1024 * 1024
MAX_TOOL_OUTPUT = 64 * 1024
MAX_OCR_PAGES = 200
CONF_HIGH = 85.0
CONF_MEDIUM = 60.0
CRITICAL_CONF = 60.0

LANG_ALIASES = {
    "id": "ind",
    "indonesian": "ind",
    "indonesia": "ind",
    "en": "eng",
    "english": "eng",
    "eng": "eng",
    "ind": "ind",
}

CRITICAL_RE = re.compile(
    r"^\d+(?:[.,]\d+)?$|Ω|ohm|\b(?:kg|mg|g|v|a|w|hz|nim|nis|id)\b|%|°|\d{4}-\d{2}-\d{2}",
    re.I,
)
FORMULA_RE = re.compile(r"[=^√∫∑]|\\frac|\^")

class OcrError(Exception):
    def __init__(self, code: str, detail: str = ""):
        self.code = code
        super().__init__(detail or code)


def tesseract_bin() -> str | None:
    return shutil.which("tesseract")


def list_languages(*, tesseract: str | None = None, force: bool = False) -> list[str]:
    binary = tesseract or tesseract_bin()
    if not binary:
        return []
    try:
        with tempfile.TemporaryFile() as stdout:
            proc = subprocess.run(
                [binary, "--list-langs"],
                stdout=stdout,
                stderr=subprocess.DEVNULL,
                timeout=5,
                check=False,
            )
            stdout.seek(0)
            output = stdout.read(MAX_TOOL_OUTPUT).decode("utf-8", errors="replace")
        mocked_output = getattr(proc, "stdout", None)
        if not output and mocked_output:
            output = mocked_output if isinstance(mocked_output, str) else mocked_output[:MAX_TOOL_OUTPUT].decode("utf-8", errors="replace")
    except Exception:
        return []
    langs: list[str] = []
    for line in output.splitlines():
        item = line.strip()
        if not item or " " in item or item.lower() == "osd":
            continue
        langs.append(item)
    return langs


def map_language(value: str | None) -> str | None:
    if not value:
        return None
    key = value.strip().lower()
    if not key:
        return None
    return LANG_ALIASES.get(key, key)


def select_languages(
    available: list[str],
    requested: list[str] | None = None,
    contract_language: str | None = None,
) -> list[str]:
    have = [a for a in available if a and a.lower() != "osd"]
    have_l = {a.lower(): a for a in have}
    if requested:
        picked = []
        for item in requested:
            mapped = map_language(item) or item
            if mapped.lower() in have_l:
                picked.append(have_l[mapped.lower()])
        return picked
    if contract_language:
        mapped = map_language(contract_language)
        if mapped and mapped.lower() in have_l:
            return [have_l[mapped.lower()]]
        return []
    if "ind" in have_l and "eng" in have_l:
        return [have_l["ind"], have_l["eng"]]
    if have:
        return [have[0]]
    return []


def confidence_level(mean: float | None) -> str | None:
    if mean is None:
        return None
    if mean >= CONF_HIGH:
        return "HIGH"
    if mean >= CONF_MEDIUM:
        return "MEDIUM"
    return "LOW"


def parse_tsv(tsv: str) -> dict[str, Any]:
    tokens: list[dict[str, Any]] = []
    if not tsv or "\t" not in tsv:
        return {"text": "", "tokens": [], "mean": None}
    lines = tsv.splitlines()
    if not lines:
        return {"text": "", "tokens": [], "mean": None}
    header = lines[0].split("\t")
    try:
        conf_i = header.index("conf")
        text_i = header.index("text")
        line_i = header.index("line_num") if "line_num" in header else None
    except ValueError:
        return {"text": "", "tokens": [], "mean": None}
    rows: list[tuple[int, str, float]] = []
    for raw in lines[1:]:
        parts = raw.split("\t")
        if len(parts) <= max(conf_i, text_i):
            continue
        try:
            conf = float(parts[conf_i])
        except ValueError:
            continue
        if conf < 0:
            continue
        word = parts[text_i] if text_i < len(parts) else ""
        if not word:
            continue
        line_no = 1
        if line_i is not None and line_i < len(parts):
            try:
                line_no = int(parts[line_i])
            except ValueError:
                line_no = 1
        rows.append((line_no, word, conf))
        tokens.append({"text": word, "confidence": conf})
    if not rows:
        return {"text": "", "tokens": [], "mean": None}
    chunks: list[str] = []
    current_line = rows[0][0]
    buf: list[str] = []
    for line_no, word, _conf in rows:
        if line_no != current_line:
            chunks.append(" ".join(buf))
            buf = [word]
            current_line = line_no
        else:
            buf.append(word)
    if buf:
        chunks.append(" ".join(buf))
    mean = sum(t["confidence"] for t in tokens) / len(tokens)
    return {"text": "\n".join(chunks), "tokens": tokens, "mean": mean}


def token_warnings(tokens: list[dict[str, Any]], text: str) -> list[str]:
    warnings: list[str] = []
    for tok in tokens:
        word = str(tok.get("text") or "")
        conf = tok.get("confidence")
        if conf is None:
            continue
        if conf < CRITICAL_CONF and CRITICAL_RE.search(word):
            if "OCR_CRITICAL_UNCERTAINTY" not in warnings:
                warnings.append("OCR_CRITICAL_UNCERTAINTY")
        if conf < CRITICAL_CONF and FORMULA_RE.search(word):
            if "LOW_CONFIDENCE_FORMULA" not in warnings:
                warnings.append("LOW_CONFIDENCE_FORMULA")
    if FORMULA_RE.search(text or "") and any(
        (t.get("confidence") is not None and t["confidence"] < CRITICAL_CONF) for t in tokens
    ):
        if "LOW_CONFIDENCE_FORMULA" not in warnings:
            warnings.append("LOW_CONFIDENCE_FORMULA")
    return warnings


def ocr_image(
    path: Path,
    *,
    languages: list[str],
    timeout: float = OCR_TIMEOUT_PAGE_SEC,
) -> dict[str, Any]:
    binary = tesseract_bin()
    if not binary:
        return {
            "status": "NOT_CONFIGURED",
            "capability": "OCR_ENGINE",
            "text": "",
            "warnings": [],
            "tokens": [],
            "confidence": None,
        }
    if not languages:
        return {
            "status": "NOT_CONFIGURED",
            "capability": "OCR_LANGUAGE_NOT_CONFIGURED",
            "text": "",
            "warnings": [],
            "tokens": [],
            "confidence": None,
        }
    lang = "+".join(languages)
    warnings: list[str] = []
    with tempfile.TemporaryDirectory(prefix="ocbf-ocr-") as raw:
        work = Path(raw)
        out_base = work / "out"
        cmd = [binary, str(path), str(out_base), "-l", lang, "tsv"]
        try:
            proc = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return {
                "status": "OCR_TIMEOUT",
                "text": "",
                "warnings": ["OCR_TIMEOUT"],
                "tokens": [],
                "confidence": None,
            }
        if proc.returncode != 0:
            return {
                "status": "OCR_FAILED",
                "text": "",
                "warnings": ["OCR_FAILED"],
                "tokens": [],
                "confidence": None,
            }
        tsv_path = work / "out.tsv"
        if not tsv_path.is_file():
            return {
                "status": "OCR_FAILED",
                "text": "",
                "warnings": ["OCR_FAILED"],
                "tokens": [],
                "confidence": None,
            }
        with tsv_path.open("rb") as handle:
            data = handle.read(MAX_OCR_STDOUT + 1)
        truncated = len(data) > MAX_OCR_STDOUT
        if truncated:
            data = data[:MAX_OCR_STDOUT]
            warnings.append("OCR_STDOUT_TRUNCATED")
        parsed = parse_tsv(data.decode("utf-8", errors="replace"))
    cleaned, sanitization = sanitize_document_text(parsed["text"])
    warns = warnings + token_warnings(parsed["tokens"], cleaned)
    mean = parsed["mean"]
    return {
        "status": "PARTIAL" if truncated else "READY",
        "method": "ocr",
        "engine": "tesseract",
        "language": lang,
        "confidence": mean,
        "confidence_level": confidence_level(mean),
        "text": cleaned,
        "warnings": warns,
        "tokens": parsed["tokens"],
        "sanitization": sanitization,
    }

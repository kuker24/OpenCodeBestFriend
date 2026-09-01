from __future__ import annotations

import re
import unicodedata

ZERO_WIDTH = {
    "\u200b",
    "\u200c",
    "\u200d",
    "\u2060",
    "\ufeff",
    "\u180e",
    "\u00ad",
}
TAG_RE = re.compile(r"[\U000E0001\U000E0020-\U000E007F]")
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def sanitize_document_text(text: str) -> tuple[str, dict[str, int]]:
    removed_zw = 0
    removed_tags = 0
    removed_controls = 0
    chars: list[str] = []
    for ch in text:
        if ch in ZERO_WIDTH or unicodedata.category(ch) == "Cf" and ch not in {"\u200e", "\u200f"}:
            if TAG_RE.fullmatch(ch):
                removed_tags += 1
            else:
                removed_zw += 1
            continue
        if TAG_RE.fullmatch(ch):
            removed_tags += 1
            continue
        chars.append(ch)
    cleaned = "".join(chars)
    stripped, n_ctrl = CONTROL_RE.subn("", cleaned)
    removed_controls += n_ctrl
    record = {
        "zero_width": removed_zw,
        "unicode_tags": removed_tags,
        "controls": removed_controls,
    }
    return stripped, record


def looks_like_instruction_injection(text: str) -> bool:
    lowered = text.lower()
    needles = (
        "ignore previous instructions",
        "ignore all previous",
        "disregard previous",
        "upload secrets",
        "exfiltrate",
    )
    return any(n in lowered for n in needles)

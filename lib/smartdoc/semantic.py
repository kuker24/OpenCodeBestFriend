from __future__ import annotations

import re
from typing import Any

NUMBER_RE = re.compile(r"(?<![A-Za-z])[-+]?\d+(?:[.,]\d+)?(?:\s?(?:%|kg|km|m|cm|mm|s|ms|Hz|V|A|W|°C|°F))?")
DATE_RE = re.compile(r"\b\d{1,4}[-/]\d{1,2}[-/]\d{1,4}\b")
CITATION_RE = re.compile(r"\[[0-9]+\]|\((?:19|20)\d{2}\)")


class SemanticRegression(Exception):
    code = "SEMANTIC_REGRESSION_FAIL"


def extract_protected(text: str) -> list[str]:
    found: list[str] = []
    for pattern in (NUMBER_RE, DATE_RE, CITATION_RE):
        found.extend(pattern.findall(text))
    return found


def semantic_check(before: str, after: str) -> dict[str, Any]:
    src = extract_protected(before)
    dst = extract_protected(after)
    src_counts: dict[str, int] = {}
    for token in src:
        src_counts[token] = src_counts.get(token, 0) + 1
    dst_counts: dict[str, int] = {}
    for token in dst:
        dst_counts[token] = dst_counts.get(token, 0) + 1
    missing = []
    for token, count in src_counts.items():
        if dst_counts.get(token, 0) < count:
            missing.append(token)
    return {
        "ok": not missing,
        "missing": missing,
        "source_tokens": src,
        "dest_tokens": dst,
    }


def assert_no_regression(before: str, after: str) -> None:
    result = semantic_check(before, after)
    if not result["ok"]:
        raise SemanticRegression(f"missing {result['missing']}")

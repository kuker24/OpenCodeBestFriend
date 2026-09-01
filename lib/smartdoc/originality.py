from __future__ import annotations

import re
from typing import Any

QUOTE_RE = re.compile(r"[\"“”](.+?)[\"“”]")
FORBIDDEN_LABELS = (
    "turnitin",
    "0% turnitin",
    "official turnitin",
    "undetectable ai",
    "bypass detector",
)

NGRAM = 5


def tokenize(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", text.lower())


def ngrams(tokens: list[str], n: int = NGRAM) -> set[tuple[str, ...]]:
    if len(tokens) < n:
        return set()
    return {tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)}


def strip_quotes(text: str) -> str:
    return QUOTE_RE.sub(" ", text)


def overlap_ratio(a: set[tuple[str, ...]], b: set[tuple[str, ...]]) -> float:
    if not a:
        return 0.0
    return len(a & b) / len(a)


def local_similarity_audit(
    text: str,
    corpus: list[dict[str, str]],
    *,
    exclude_quotes: bool = True,
) -> dict[str, Any]:
    source = strip_quotes(text) if exclude_quotes else text
    src_grams = ngrams(tokenize(source))
    matches: list[dict[str, Any]] = []
    ids: list[str] = []
    for item in corpus:
        cid = str(item.get("id") or "")
        ids.append(cid)
        body = str(item.get("text") or "")
        grams = ngrams(tokenize(body))
        ratio = overlap_ratio(src_grams, grams)
        shared = src_grams & grams
        sample = [" ".join(g) for g in list(shared)[:8]]
        matches.append(
            {
                "id": cid,
                "ratio": round(ratio, 4),
                "shared_ngrams": len(shared),
                "sample": sample,
            }
        )
    matches.sort(key=lambda row: row["ratio"], reverse=True)
    peak = matches[0]["ratio"] if matches else 0.0
    return {
        "label": "Local Similarity Audit",
        "corpus": ids,
        "score": round(peak, 4),
        "matches": matches,
    }


def contains_forbidden_product_language(text: str) -> list[str]:
    lowered = text.lower()
    return [label for label in FORBIDDEN_LABELS if label in lowered]

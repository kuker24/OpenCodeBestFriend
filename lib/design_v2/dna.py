from __future__ import annotations

import re
from typing import Any

TOKEN = re.compile(r"[a-z0-9]+")

AESTHETIC_MAP = {
    "minimal": "minimal",
    "clean": "minimal",
    "swiss": "minimal",
    "quiet": "minimal",
    "editorial": "editorial",
    "magazine": "editorial",
    "serif": "editorial",
    "futuristic": "futuristic",
    "cyber": "futuristic",
    "neon": "futuristic",
    "brutalist": "brutalist",
    "raw": "brutalist",
    "concrete": "brutalist",
    "luxury": "luxury",
    "premium": "luxury",
    "playful": "playful",
    "fun": "playful",
    "cartoon": "playful",
    "dark": "dark",
    "midnight": "dark",
    "noir": "dark",
}
DENSITY_MAP = {
    "sparse": "sparse",
    "airy": "sparse",
    "balanced": "balanced",
    "dense": "dense",
    "compact": "dense",
    "crowded": "dense",
}
GEOMETRY_MAP = {
    "sharp": "sharp",
    "rectilinear": "sharp",
    "rounded": "rounded",
    "soft": "rounded",
    "organic": "organic",
}
MOTION_MAP = {
    "stagger": "stagger",
    "ambient": "ambient",
    "parallax": "parallax",
    "subtle": "subtle",
    "none": "none",
}
FIT_MAP = {
    "ai": "ai",
    "saas": "saas",
    "security": "security",
    "cyber": "security",
    "cybersecurity": "security",
    "dashboard": "dashboard",
    "ops": "dashboard",
    "developer": "developer-tools",
    "devtools": "developer-tools",
}
COMPLEXITY_MAP = {
    "simple": "low",
    "quiet": "low",
    "busy": "high",
    "complex": "high",
}
SLOP_QUERY = {
    "glass": "excessive-glassmorphism",
    "glassmorphism": "excessive-glassmorphism",
    "glow": "excessive-glow",
    "blob": "floating-gradient-blobs",
    "blobs": "floating-gradient-blobs",
    "bento": "random-bento",
    "gradient": "purple-blue-gradient",
    "aurora": "floating-gradient-blobs",
}
AVOID_HINTS = frozenset({"no", "not", "without", "jangan", "avoid", "slop", "generic"})


def tokenize(text: str) -> list[str]:
    return TOKEN.findall(text.lower())


def extract_query(query: str) -> dict[str, Any]:
    tokens = tokenize(query)
    token_set = set(tokens)
    aesthetic = sorted({AESTHETIC_MAP[t] for t in tokens if t in AESTHETIC_MAP})
    density = next((DENSITY_MAP[t] for t in tokens if t in DENSITY_MAP), None)
    geometry = next((GEOMETRY_MAP[t] for t in tokens if t in GEOMETRY_MAP), None)
    motion = sorted({MOTION_MAP[t] for t in tokens if t in MOTION_MAP})
    product_fit = sorted({FIT_MAP[t] for t in tokens if t in FIT_MAP})
    complexity = next((COMPLEXITY_MAP[t] for t in tokens if t in COMPLEXITY_MAP), None)
    wants_slop = sorted({SLOP_QUERY[t] for t in tokens if t in SLOP_QUERY})
    avoid = bool(token_set & AVOID_HINTS)
    return {
        "aesthetic": aesthetic,
        "density": density,
        "geometry": geometry,
        "motion": motion,
        "product_fit": product_fit,
        "visual_complexity": complexity,
        "wants_slop": wants_slop if not avoid else [],
        "avoid_slop": avoid,
        "tokens": tokens,
    }


def score_dna(item: dict[str, Any], extracted: dict[str, Any], policy: dict[str, Any]) -> float:
    raw = item.get("dna")
    dna: dict[str, Any] = raw if isinstance(raw, dict) else {}
    weight = float(((policy.get("search") or {}).get("weights") or {}).get("dna") or 5.0)
    score = 0.0
    item_aes = set(dna.get("aesthetic") or [])
    if extracted["aesthetic"] and item_aes:
        score += weight * len(item_aes & set(extracted["aesthetic"])) / max(len(extracted["aesthetic"]), 1)
    if extracted["density"] and dna.get("density"):
        score += 2.0 if dna.get("density") == extracted["density"] else -1.0
    if extracted["geometry"] and dna.get("geometry"):
        score += 1.5 if dna.get("geometry") == extracted["geometry"] else 0.0
    item_fit = set(item.get("product_fit") or dna.get("product_fit") or [])
    if extracted["product_fit"] and item_fit:
        score += 3.0 * len(item_fit & set(extracted["product_fit"])) / max(len(extracted["product_fit"]), 1)
    item_motion = set(dna.get("motion") or [])
    if extracted["motion"] and item_motion:
        score += 1.0 * len(item_motion & set(extracted["motion"]))
    return score


def slop_penalty(item: dict[str, Any], extracted: dict[str, Any], policy: dict[str, Any]) -> float:
    flags = set(item.get("anti_slop") or [])
    tags = set(tokenize(" ".join(item.get("tags") or [])))
    known = set((policy.get("anti_slop") or []))
    present = flags | (tags & known)
    if not present:
        return 0.0
    penalty = float((policy.get("search") or {}).get("anti_slop_penalty") or 3.0)
    if extracted.get("avoid_slop"):
        return penalty * len(present)
    wanted = set(extracted.get("wants_slop") or [])
    extra = present - wanted
    if not extra:
        return 0.0
    return penalty * 0.5 * len(extra)

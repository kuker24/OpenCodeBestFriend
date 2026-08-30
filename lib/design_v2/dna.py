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
    "light": "light",
    "bright": "light",
    "industrial": "industrial",
    "utilitarian": "industrial",
    "technical": "technical",
    "terminal": "technical",
    "corporate": "corporate",
    "enterprise": "corporate",
    "organic": "organic",
    "natural": "organic",
    "retro": "retro",
    "vintage": "retro",
    "y2k": "neo-y2k",
    "glass": "glass",
    "glassmorphism": "glass",
    "monochrome": "monochrome",
    "monochromatic": "monochrome",
    "contrast": "high-contrast",
    "soft": "soft",
    "calm": "soft",
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
    "reduced": "reduced",
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
    "terminal": "developer-tools",
    "financial": "finance",
    "finance": "finance",
    "fintech": "finance",
    "banking": "finance",
    "fashion": "fashion",
    "ecommerce": "ecommerce",
    "commerce": "ecommerce",
    "shopping": "ecommerce",
    "education": "education",
    "learning": "education",
    "government": "public-service",
    "public": "public-service",
    "civic": "public-service",
    "healthcare": "healthcare",
    "health": "healthcare",
    "medical": "healthcare",
    "enterprise": "enterprise",
}
COMPLEXITY_MAP = {
    "simple": "low",
    "quiet": "low",
    "busy": "high",
    "complex": "high",
    "balanced": "medium",
}
TYPOGRAPHY_MAP = {
    "serif": "serif",
    "sans": "sans-serif",
    "sans-serif": "sans-serif",
    "mono": "monospace",
    "monospace": "monospace",
    "terminal": "monospace",
    "display": "display",
    "humanist": "humanist",
}
SPACING_MAP = {
    "tight": "tight",
    "compact": "tight",
    "generous": "generous",
    "airy": "generous",
    "rhythmic": "rhythmic",
}
COLOR_MAP = {
    "monochrome": "monochrome",
    "monochromatic": "monochrome",
    "colorful": "colorful",
    "colourful": "colorful",
    "muted": "muted",
    "dark": "dark",
    "light": "light",
    "contrast": "high-contrast",
    "warm": "warm",
    "cool": "cool",
}
HIERARCHY_MAP = {
    "strong": "strong",
    "bold": "strong",
    "restrained": "restrained",
    "subtle": "restrained",
    "layered": "layered",
}
LAYOUT_MAP = {
    "grid": "grid",
    "split": "split",
    "sidebar": "sidebar",
    "stacked": "stacked",
    "editorial": "editorial",
    "dashboard": "dashboard",
}
INTERACTION_MAP = {
    "hover": "hover",
    "keyboard": "keyboard",
    "drag": "drag",
    "touch": "touch",
    "form": "form",
    "command": "command-palette",
}
RESPONSIVE_MAP = {
    "responsive": "responsive",
    "mobile-first": "mobile-first",
    "mobile": "mobile-first",
    "adaptive": "adaptive",
    "fluid": "fluid",
}
CONTENT_STYLE_MAP = {
    "technical": "technical",
    "terminal": "technical",
    "editorial": "editorial",
    "concise": "concise",
    "dense": "data-heavy",
    "trustworthy": "trustworthy",
    "professional": "professional",
    "friendly": "friendly",
}
ACCESSIBILITY_MAP = {
    "accessible": "accessible",
    "accessibility": "accessible",
    "wcag": "wcag",
    "keyboard": "keyboard",
    "contrast": "high-contrast",
    "reduced": "reduced-motion",
    "reduced-motion": "reduced-motion",
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
    "pill": "pill-everything",
    "generic": "generic-saas-hero",
    "metrics": "fake-metrics",
}
NEGATIONS = frozenset({"no", "not", "without", "jangan", "avoid"})


def _mapped(tokens: list[str], mapping: dict[str, str]) -> list[str]:
    return sorted({mapping[token] for token in tokens if token in mapping})


def _first(tokens: list[str], mapping: dict[str, str]) -> str | None:
    return next((mapping[token] for token in tokens if token in mapping), None)


def tokenize(text: str) -> list[str]:
    return TOKEN.findall(text.lower())


def extract_query(query: str) -> dict[str, Any]:
    tokens = tokenize(query)
    wanted_slop: set[str] = set()
    avoided_slop: set[str] = set()
    for index, token in enumerate(tokens):
        flag = SLOP_QUERY.get(token)
        if not flag:
            continue
        previous = set(tokens[max(0, index - 2) : index])
        if previous & NEGATIONS:
            avoided_slop.add(flag)
        else:
            wanted_slop.add(flag)
    avoid_all = any(
        tokens[index] == "slop" and set(tokens[max(0, index - 2) : index]) & NEGATIONS
        for index in range(len(tokens))
    )
    return {
        "aesthetic": _mapped(tokens, AESTHETIC_MAP),
        "density": _first(tokens, DENSITY_MAP),
        "geometry": _first(tokens, GEOMETRY_MAP),
        "typography": _mapped(tokens, TYPOGRAPHY_MAP),
        "spacing": _first(tokens, SPACING_MAP),
        "color": _mapped(tokens, COLOR_MAP),
        "hierarchy": _mapped(tokens, HIERARCHY_MAP),
        "layout": _mapped(tokens, LAYOUT_MAP),
        "motion": _mapped(tokens, MOTION_MAP),
        "interaction": _mapped(tokens, INTERACTION_MAP),
        "responsive_behavior": _mapped(tokens, RESPONSIVE_MAP),
        "product_fit": _mapped(tokens, FIT_MAP),
        "content_style": _mapped(tokens, CONTENT_STYLE_MAP),
        "visual_complexity": _first(tokens, COMPLEXITY_MAP),
        "accessibility": _mapped(tokens, ACCESSIBILITY_MAP),
        "wants_slop": sorted(wanted_slop - avoided_slop),
        "avoid_slop": avoid_all or bool(avoided_slop),
        "avoid_all_slop": avoid_all,
        "avoid_slop_flags": sorted(avoided_slop),
        "tokens": tokens,
    }


def score_dna(item: dict[str, Any], extracted: dict[str, Any], policy: dict[str, Any]) -> float:
    raw = item.get("dna")
    dna: dict[str, Any] = raw if isinstance(raw, dict) else {}
    search_cfg = policy.get("search") or {}
    default_weight = float((search_cfg.get("weights") or {}).get("dna") or 5.0)
    dimension_weights = search_cfg.get("dna_dimension_weights") or {}
    score = 0.0

    for dimension in (
        "aesthetic",
        "density",
        "geometry",
        "typography",
        "spacing",
        "color",
        "hierarchy",
        "layout",
        "motion",
        "interaction",
        "responsive_behavior",
        "content_style",
        "visual_complexity",
        "accessibility",
    ):
        requested = extracted.get(dimension)
        actual = dna.get(dimension)
        if not requested or not actual:
            continue
        requested_values = set(requested if isinstance(requested, list) else [requested])
        actual_values = set(actual if isinstance(actual, list) else [actual])
        overlap = requested_values & actual_values
        if overlap:
            weight = float(dimension_weights.get(dimension) or (default_weight if dimension == "aesthetic" else 1.0))
            score += weight * len(overlap) / len(requested_values)
        elif dimension == "density":
            score -= 1.0

    item_fit = set(item.get("product_fit") or dna.get("product_fit") or [])
    if extracted["product_fit"] and item_fit:
        requested_fit = set(extracted["product_fit"])
        overlap = item_fit & requested_fit
        if overlap:
            score += float(search_cfg.get("product_fit_match") or 6.0) * len(overlap) / len(requested_fit)
        else:
            score -= float(search_cfg.get("product_fit_mismatch") or 2.0)
    return score


def slop_penalty(item: dict[str, Any], extracted: dict[str, Any], policy: dict[str, Any]) -> float:
    flags = set(item.get("anti_slop") or [])
    known = set((policy.get("anti_slop") or []))
    tag_flags = {str(tag) for tag in item.get("tags") or [] if str(tag) in known}
    present = flags | tag_flags
    if not present:
        return 0.0
    penalty = float((policy.get("search") or {}).get("anti_slop_penalty") or 3.0)
    if extracted.get("avoid_all_slop"):
        return penalty * len(present)
    wanted = set(extracted.get("wants_slop") or [])
    avoided = set(extracted.get("avoid_slop_flags") or [])
    explicit = present & avoided
    extra = present - wanted - avoided
    return penalty * len(explicit) + penalty * 0.5 * len(extra)

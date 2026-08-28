from __future__ import annotations

from pathlib import Path

from .common import bf_dir, load_json, product_version, share_dir

EXPECTED_PRODUCT = "opencode-bestfriend"
EXPECTED_REPO = "https://github.com/kuker24/OpenCodeBestFriend"
LEGACY_REPO_NEEDLE = "ClaudeBestFriend"
LEGACY_VERSION_NEEDLE = "claude"
AGENTS_BEGIN = "<!-- OPENCODEBESTFRIEND:BEGIN -->"
AGENTS_END = "<!-- OPENCODEBESTFRIEND:END -->"


def owned_agents_block(text: str) -> str | None:
    if AGENTS_BEGIN not in text or AGENTS_END not in text:
        return None
    start = text.index(AGENTS_BEGIN)
    end = text.index(AGENTS_END) + len(AGENTS_END)
    if end <= start:
        return None
    return text[start:end]


def ownership_path() -> Path:
    return bf_dir() / "manifests" / "ownership.json"


def load_ownership() -> dict | None:
    path = ownership_path()
    if not path.is_file():
        return None
    try:
        data = load_json(path)
    except (OSError, ValueError):
        return {"__malformed": True}
    if not isinstance(data, dict):
        return {"__malformed": True}
    return data


def detect_legacy_overlay() -> dict | None:
    source_clone = share_dir() / "source" / "ClaudeBestFriend"
    data = load_ownership()
    if data is None:
        if source_clone.is_dir():
            return {"fromProduct": "ClaudeBestFriend", "fromVersion": "unknown"}
        return None
    if data.get("__malformed"):
        return {"fromProduct": "unknown", "fromVersion": "malformed"}
    repo = str(data.get("sourceRepository") or "")
    product = str(data.get("product") or "")
    source_ver = str(data.get("sourceVersion") or "")
    installed_ver = data.get("productVersion")
    if LEGACY_REPO_NEEDLE in repo or LEGACY_VERSION_NEEDLE in source_ver.lower():
        return {
            "fromProduct": "ClaudeBestFriend",
            "fromVersion": source_ver or installed_ver or "unknown",
        }
    if product and product != EXPECTED_PRODUCT:
        return {"fromProduct": product, "fromVersion": str(installed_ver or source_ver or "unknown")}
    if not installed_ver:
        return {"fromProduct": product or "unknown", "fromVersion": source_ver or "unknown"}
    if source_clone.is_dir() and LEGACY_REPO_NEEDLE in repo:
        return {"fromProduct": "ClaudeBestFriend", "fromVersion": source_ver or "unknown"}
    return None


def identity_findings(expected_version: str | None = None) -> list[tuple[str, str, str]]:
    expected_version = expected_version or product_version()
    out: list[tuple[str, str, str]] = []
    data = load_ownership()
    if data is None:
        out.append(("FAIL", "INSTALLED_PRODUCT", "missing ownership.json"))
        out.append(("FAIL", "INSTALLED_VERSION", f"expected={expected_version} actual=missing"))
        out.append(("FAIL", "SOURCE_REPOSITORY", "missing"))
        return out
    if data.get("__malformed"):
        out.append(("FAIL", "INSTALLED_PRODUCT", "malformed ownership.json"))
        out.append(("FAIL", "INSTALLED_VERSION", "malformed"))
        out.append(("FAIL", "SOURCE_REPOSITORY", "malformed"))
        return out
    product = str(data.get("product") or "")
    actual_ver = str(data.get("productVersion") or "")
    repo = str(data.get("sourceRepository") or "")
    if product != EXPECTED_PRODUCT:
        out.append(("FAIL", "INSTALLED_PRODUCT", f"expected={EXPECTED_PRODUCT} actual={product or 'missing'}"))
    else:
        out.append(("PASS", "INSTALLED_PRODUCT", product))
    if actual_ver != expected_version:
        out.append(
            (
                "FAIL",
                "INSTALLED_VERSION",
                f"expected={expected_version} actual={actual_ver or 'missing'}",
            )
        )
    else:
        out.append(("PASS", "INSTALLED_VERSION", actual_ver))
    if repo != EXPECTED_REPO:
        out.append(("FAIL", "SOURCE_REPOSITORY", f"expected={EXPECTED_REPO} actual={repo or 'missing'}"))
    else:
        out.append(("PASS", "SOURCE_REPOSITORY", repo))
    return out

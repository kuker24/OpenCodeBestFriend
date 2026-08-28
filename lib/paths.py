from __future__ import annotations

import os
import re
from pathlib import Path

from .common import bin_dir, config_dir, die, share_dir

STAMP_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
HELPER_NAMES = frozenset({"opencode-bf", "opencode-chromium-cdp"})


def _is_within(child: Path, root: Path) -> bool:
    try:
        child.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def allowed_roots() -> list[Path]:
    return [config_dir(), share_dir(), bin_dir()]


def assert_within_allowed(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    for root in allowed_roots():
        if root.exists() and (_is_within(resolved, root) or resolved == root.resolve()):
            return resolved
        if not root.exists():
            parent = root.parent
            if parent.exists() and (_is_within(resolved, parent) or resolved == parent.resolve()):
                if resolved == root or _is_within(resolved, root) or str(resolved).startswith(str(root)):
                    return resolved
    die(f"PATH_OUTSIDE_OWNED_NAMESPACE {path}")
    raise SystemExit(1)


def assert_helper_name(name: str) -> None:
    if name not in HELPER_NAMES:
        die(f"INVALID_HELPER_NAME {name}")


def assert_skill_name(name: str) -> None:
    if not NAME_RE.fullmatch(name):
        die(f"MALICIOUS_OWNERSHIP_NAME {name}")


def resolve_under(root: Path, name: str) -> Path:
    assert_skill_name(name)
    base = root.resolve()
    dest = (root / name).resolve()
    if dest != base and not _is_within(dest, base):
        die(f"PATH_ESCAPE {name}")
    return dest


def resolve_backup_stamp(stamp: str, backups: Path) -> Path:
    if not STAMP_RE.fullmatch(stamp):
        die(f"INVALID_BACKUP_STAMP {stamp}")
    root = backups.resolve()
    src = (backups / stamp).resolve()
    if src != root and not _is_within(src, root):
        die(f"BACKUP_PATH_ESCAPE {stamp}")
    if not src.is_dir():
        die(f"backup not found {stamp}")
    return src


def tar_member_ok(dest: Path, name: str) -> bool:
    dest = dest.resolve()
    cleaned = name.replace("\\", "/")
    if not cleaned or cleaned in {".", ".."}:
        return False
    if cleaned.startswith("/") or cleaned.startswith("~"):
        return False
    if re.match(r"^[A-Za-z]:", cleaned):
        return False
    parts = Path(cleaned).parts
    if ".." in parts:
        return False
    try:
        target = (dest / cleaned).resolve()
    except (OSError, RuntimeError):
        return False
    dest_s = str(dest)
    return target == dest or str(target).startswith(dest_s + os.sep)

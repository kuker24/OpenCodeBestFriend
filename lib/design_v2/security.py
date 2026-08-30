from __future__ import annotations

import os
import re
import stat
import zipfile
from pathlib import Path
from typing import Any

from .bank import DesignV2Error

WIN_ABS = re.compile(r"^[A-Za-z]:")


class SecurityError(DesignV2Error):
    code = "SECURITY"


def compile_secret_patterns(policy: dict[str, Any]) -> list[re.Pattern[str]]:
    compiled: list[re.Pattern[str]] = []
    for parts in policy.get("secret_pattern_parts") or []:
        compiled.append(re.compile("".join(str(p) for p in parts), re.IGNORECASE))
    return compiled


def member_ok(name: str) -> bool:
    cleaned = name.replace("\\", "/")
    if not cleaned or cleaned in {".", ".."}:
        return False
    if cleaned.startswith("/") or cleaned.startswith("~"):
        return False
    if WIN_ABS.match(cleaned):
        return False
    parts = Path(cleaned).parts
    if ".." in parts:
        return False
    return True


def lstat_info(path: Path) -> os.stat_result:
    return path.lstat()


def classify_stat(st: os.stat_result) -> str | None:
    if stat.S_ISLNK(st.st_mode):
        return "symlink"
    if stat.S_ISDIR(st.st_mode):
        return None
    if not stat.S_ISREG(st.st_mode):
        return "special"
    if st.st_nlink > 1:
        return "hardlink"
    return None


def inspect_path(path: Path, policy: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    try:
        st = lstat_info(path)
    except OSError:
        return ["missing"]
    kind = classify_stat(st)
    if kind:
        issues.append(kind)
    limits = policy.get("import") or {}
    max_file = int(limits.get("max_file_bytes") or 10485760)
    if stat.S_ISREG(st.st_mode) and st.st_size > max_file:
        issues.append("too_large")
    return issues


def inspect_tree(path: Path, policy: dict[str, Any]) -> list[str]:
    issues = inspect_path(path, policy)
    if issues:
        return issues
    st = lstat_info(path)
    if not stat.S_ISDIR(st.st_mode):
        return issues
    limits = policy.get("import") or {}
    max_files = int(limits.get("max_files") or 2000)
    max_total = int(limits.get("max_total_bytes") or 104857600)
    max_file = int(limits.get("max_file_bytes") or 10485760)
    files = 0
    total = 0
    for dirpath, dirnames, filenames in os.walk(path, followlinks=False):
        current = Path(dirpath)
        if current.is_symlink():
            return ["symlink"]
        kept: list[str] = []
        for name in dirnames:
            child = current / name
            try:
                cst = child.lstat()
            except OSError:
                return ["unreadable"]
            if stat.S_ISLNK(cst.st_mode):
                return ["symlink"]
            kept.append(name)
        dirnames[:] = kept
        for name in filenames:
            child = current / name
            try:
                cst = child.lstat()
            except OSError:
                return ["unreadable"]
            bad = classify_stat(cst)
            if bad:
                return [bad]
            files += 1
            total += cst.st_size
            if cst.st_size > max_file:
                return ["too_large"]
            if files > max_files or total > max_total:
                return ["too_large"]
    return issues


def inspect_zip(path: Path, policy: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    zlim = policy.get("zip") or {}
    max_members = int(zlim.get("max_members") or 20000)
    max_member = int(zlim.get("max_member_uncompressed") or 52428800)
    max_total = int(zlim.get("max_total_uncompressed") or 2147483648)
    max_ratio = float(zlim.get("max_compression_ratio") or 200)
    try:
        with zipfile.ZipFile(path) as handle:
            infos = handle.infolist()
    except zipfile.BadZipFile:
        return ["bad_zip"]
    if len(infos) > max_members:
        return ["zip_members"]
    total = 0
    for info in infos:
        if info.filename.endswith("/"):
            continue
        if not member_ok(info.filename):
            return ["zip_traversal"]
        if info.is_dir():
            continue
        if stat.S_ISLNK(info.external_attr >> 16):
            return ["symlink"]
        uncompressed = int(info.file_size)
        compressed = max(int(info.compress_size), 1)
        if uncompressed > max_member:
            return ["zip_member_size"]
        if uncompressed / compressed > max_ratio:
            return ["zip_ratio"]
        total += uncompressed
        if total > max_total:
            return ["zip_total"]
    return issues


def allowed_extension(name: str, policy: dict[str, Any]) -> bool:
    allowed = {str(ext).lower() for ext in (policy.get("allowed_extensions") or [])}
    suffix = Path(name).suffix.lower()
    if not suffix:
        return Path(name).name.lower() in {"license", "copying", "design.md", "manifest.json"}
    return suffix in allowed


def secret_hits(text: str, patterns: list[re.Pattern[str]]) -> bool:
    return any(pat.search(text) for pat in patterns)


def scan_file_secrets(path: Path, policy: dict[str, Any], patterns: list[re.Pattern[str]]) -> bool:
    max_read = int((policy.get("import") or {}).get("max_file_bytes") or 10485760)
    try:
        with path.open("rb") as handle:
            data = handle.read(max_read + 1)
    except OSError:
        return True
    if len(data) > max_read:
        return True
    if b"\x00" in data:
        return False
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return secret_hits(text, patterns)

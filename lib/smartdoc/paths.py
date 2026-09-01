from __future__ import annotations

import json
import os
import re
import tempfile
from collections.abc import Mapping
from pathlib import Path

from . import DEFAULT_DIRNAME, ENV_VAR

WIN_ABS = re.compile(r"^[A-Za-z]:")
UNSAFE_FILENAME = re.compile(r'[\x00-\x1f<>:"/\\|?*]')
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


class PathEscape(Exception):
    code = "PATH_ESCAPE"


class CollisionError(Exception):
    code = "OUTPUT_EXISTS"


def home(home_dir: Path | None = None) -> Path:
    if home_dir is not None:
        return Path(home_dir).expanduser()
    return Path(os.environ.get("HOME") or str(Path.home())).expanduser()


def resolve_smartdoc_root(
    explicit: str | None = None,
    env: Mapping[str, str] | None = None,
    home_dir: Path | None = None,
) -> Path:
    environ = env if env is not None else os.environ
    if explicit:
        return Path(explicit).expanduser().resolve()
    raw = environ.get(ENV_VAR)
    if raw:
        return Path(raw).expanduser().resolve()
    return (home(home_dir) / DEFAULT_DIRNAME).expanduser().resolve()


def is_within(child: Path, root: Path) -> bool:
    try:
        child.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def assert_under_root(root: Path, path: Path) -> Path:
    base = root.expanduser().resolve()
    try:
        resolved = path.expanduser().resolve()
    except OSError as exc:
        raise PathEscape(f"unresolvable path {path}") from exc
    if resolved != base and not is_within(resolved, base):
        raise PathEscape(f"PATH_ESCAPE {path}")
    return resolved


def layout(root: Path) -> dict[str, Path]:
    return {
        "root": root,
        "profiles": root / "profiles",
        "styles": root / "styles",
        "fonts": root / "fonts",
        "books": root / "books",
    }


def ensure_dir(path: Path, *, mode: int = 0o700) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(path, mode)
    except OSError:
        pass
    return path


def ensure_root(root: Path) -> dict[str, Path]:
    ensure_dir(root)
    mapped = layout(root)
    for key, path in mapped.items():
        if key != "root":
            ensure_dir(path)
    return mapped


def archive_member_ok(name: str) -> bool:
    cleaned = name.replace("\\", "/")
    if not cleaned or cleaned in {".", ".."}:
        return False
    if cleaned.startswith("/") or cleaned.startswith("~"):
        return False
    if WIN_ABS.match(cleaned):
        return False
    if ".." in Path(cleaned).parts:
        return False
    return True


def assert_skill_like_name(name: str) -> str:
    if not NAME_RE.fullmatch(name):
        raise PathEscape(f"INVALID_NAME {name}")
    return name


def safe_filename(name: str) -> str:
    cleaned = name.replace("\\", "/").split("/")[-1]
    cleaned = UNSAFE_FILENAME.sub("-", cleaned).strip(" .")
    cleaned = re.sub(r"-{2,}", "-", cleaned)
    if not cleaned or cleaned in {".", ".."}:
        return "document"
    if cleaned.startswith("-"):
        cleaned = "f" + cleaned
    return cleaned[:180]


def resolve_output_path(directory: Path, filename: str, *, overwrite: bool = False) -> Path:
    dest_dir = directory.expanduser().resolve()
    dest = dest_dir / safe_filename(filename)
    if overwrite:
        return dest
    if not dest.exists():
        return dest
    stem = dest.stem
    suffix = dest.suffix
    n = 1
    while True:
        candidate = dest_dir / f"{stem}-{n}{suffix}"
        if not candidate.exists():
            return candidate
        n += 1
        if n > 9999:
            raise CollisionError(str(dest))


def atomic_write(path: Path, data: bytes, *, mode: int = 0o600) -> None:
    parent = path.parent
    ensure_dir(parent)
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", dir=str(parent))
    tmp_path = Path(tmp)
    try:
        os.write(fd, data)
        os.fsync(fd)
        os.close(fd)
        fd = -1
        try:
            os.chmod(tmp_path, mode)
        except OSError:
            pass
        os.replace(tmp_path, path)
        try:
            os.chmod(path, mode)
        except OSError:
            pass
    finally:
        if fd >= 0:
            os.close(fd)
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass


def write_json_private(path: Path, payload) -> None:
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    atomic_write(path, text.encode("utf-8"), mode=0o600)

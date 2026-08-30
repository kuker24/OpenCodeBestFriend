from __future__ import annotations

import json
import os
from pathlib import Path
from collections.abc import Mapping
from typing import Any

from . import ENV_VAR, ENV_VAR_LEGACY, PACKAGE_DIR, SKIP_FTS_VAR, SKIP_FTS_VAR_LEGACY

KIND_DIRS = (
    "systems",
    "templates",
    "pages",
    "sections",
    "blocks",
    "components",
    "primitives",
    "themes",
    "backgrounds",
    "effects",
    "motion",
    "patterns",
)
SOURCE_PROVIDERS = ("aura", "21st", "open-design", "github-oss", "refero", "motionsites", "manual")


class DesignV2Error(Exception):
    code = "DESIGN_V2_ERROR"

    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        if code:
            self.code = code


class PathEscape(DesignV2Error):
    code = "PATH_ESCAPE"


def load_policy() -> dict[str, Any]:
    return json.loads((PACKAGE_DIR / "policy.json").read_text(encoding="utf-8"))


def home() -> Path:
    return Path(os.environ.get("HOME") or str(Path.home())).expanduser()


def env_get(canonical: str, environ: Mapping[str, str] | None = None) -> str | None:
    names = {
        ENV_VAR: (ENV_VAR, ENV_VAR_LEGACY),
        SKIP_FTS_VAR: (SKIP_FTS_VAR, SKIP_FTS_VAR_LEGACY),
    }.get(canonical, (canonical,))
    lookup = environ if environ is not None else os.environ
    for name in names:
        raw = lookup.get(name)
        if raw:
            return raw
    return None


def resolve_design_v2_root(
    explicit: str | None = None,
    env: Mapping[str, str] | None = None,
    home_dir: Path | None = None,
) -> Path:
    environ = env if env is not None else os.environ
    if explicit:
        return Path(explicit).expanduser().resolve()
    raw = env_get(ENV_VAR, environ)
    if raw:
        return Path(raw).expanduser().resolve()
    root = home_dir if home_dir is not None else home()
    return (root / "DesignV2").expanduser().resolve()


def _is_within(child: Path, root: Path) -> bool:
    try:
        child.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def assert_under_v2(root: Path, path: Path) -> Path:
    base = root.expanduser().resolve()
    resolved = path.expanduser()
    try:
        resolved = resolved.resolve()
    except OSError as exc:
        raise PathEscape(f"unresolvable path {path}") from exc
    if resolved != base and not _is_within(resolved, base):
        raise PathEscape(f"PATH_ESCAPE {path}")
    return resolved


def layout_map(root: Path) -> dict[str, Path]:
    return {
        "root": root,
        "catalog": root / "catalog",
        "inbox": root / "inbox",
        "sources": root / "sources",
        "quarantine": root / "quarantine",
        "reports": root / "reports",
        "tmp": root / ".tmp",
    }


def catalog_ready(root: Path) -> bool:
    lock = root / "catalog" / "catalog.lock.json"
    return lock.is_file()


def bank_present(root: Path) -> bool:
    return root.is_dir()


def ensure_layout(root: Path) -> dict[str, Path]:
    dirs = layout_map(root)
    for key in ("catalog", "inbox", "sources", "quarantine", "reports", "tmp"):
        dirs[key].mkdir(parents=True, exist_ok=True)
    for name in SOURCE_PROVIDERS:
        (dirs["sources"] / name).mkdir(parents=True, exist_ok=True)
    for name in KIND_DIRS:
        (root / name).mkdir(parents=True, exist_ok=True)
    return dirs


def read_lock(root: Path) -> dict[str, Any] | None:
    path = root / "catalog" / "catalog.lock.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def jsonl_path(root: Path, lock: dict[str, Any] | None = None) -> Path | None:
    doc = lock if lock is not None else read_lock(root)
    if not doc:
        return None
    name = str(doc.get("jsonl_filename") or "")
    if not name or "/" in name or ".." in name:
        return None
    path = root / "catalog" / name
    try:
        assert_under_v2(root, path)
    except PathEscape:
        return None
    return path if path.is_file() else None


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def list_sources(root: Path | None = None) -> dict[str, Any]:
    bank = root if root is not None else resolve_design_v2_root()
    if not bank_present(bank):
        return {"status": "EMPTY", "root": str(bank), "providers": [], "offline": True}
    providers: list[dict[str, Any]] = []
    for name in SOURCE_PROVIDERS:
        base = bank / "sources" / name
        pointer = None
        pointer_path = base / "pointer.json"
        if pointer_path.is_file():
            try:
                loaded = json.loads(pointer_path.read_text(encoding="utf-8"))
                pointer = loaded if isinstance(loaded, dict) else None
            except (OSError, json.JSONDecodeError, UnicodeDecodeError):
                pointer = {"error": "unreadable"}
        entries: list[dict[str, Any]] = []
        if base.is_dir():
            for child in sorted(base.iterdir()):
                if child.is_dir():
                    entries.append(
                        {
                            "id": child.name,
                            "source_id": child.name,
                            "ingested": (child / "ingested.json").is_file(),
                        }
                    )
        providers.append(
            {
                "provider": name,
                "count": len(entries),
                "pointer": pointer,
                "sources": entries,
            }
        )
    return {"status": "ok", "root": str(bank), "providers": providers, "offline": True}

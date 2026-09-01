from __future__ import annotations

from typing import Any

import json
from pathlib import Path

from .paths import (
    PathEscape,
    assert_skill_like_name,
    assert_under_root,
    ensure_root,
    layout,
    write_json_private,
)


SELECTED_NAME = "_selected.json"


def _profiles_dir(root: Path) -> Path:
    mapped = ensure_root(root)
    return mapped["profiles"]


def _profile_file(root: Path, name: str) -> Path:
    assert_skill_like_name(name)
    return assert_under_root(root, _profiles_dir(root) / f"{name}.json")


def _selected_file(root: Path) -> Path:
    return assert_under_root(root, _profiles_dir(root) / SELECTED_NAME)


def _normalize_identity(identity: Any) -> list[dict[str, str]]:
    if not isinstance(identity, list):
        raise PathEscape("INVALID_IDENTITY")
    out: list[dict[str, str]] = []
    for item in identity:
        if not isinstance(item, dict):
            raise PathEscape("INVALID_IDENTITY")
        label = str(item.get("label") or "").strip()
        value = str(item.get("value") or "")
        if not label:
            raise PathEscape("INVALID_IDENTITY")
        out.append({"label": label, "value": value})
    return out


def create_profile(root: Path, name: str, identity: list[dict[str, str]] | None = None) -> dict[str, Any]:
    path = _profile_file(root, name)
    if path.exists():
        raise PathEscape(f"PROFILE_EXISTS {name}")
    payload = {"profileName": name, "identity": _normalize_identity(identity or [])}
    write_json_private(path, payload)
    return payload


def update_profile(root: Path, name: str, identity: list[dict[str, str]]) -> dict[str, Any]:
    path = _profile_file(root, name)
    if not path.is_file():
        raise PathEscape(f"PROFILE_MISSING {name}")
    payload = {"profileName": name, "identity": _normalize_identity(identity)}
    write_json_private(path, payload)
    return payload


def load_profile(root: Path, name: str) -> dict[str, Any]:
    path = _profile_file(root, name)
    if not path.is_file():
        raise PathEscape(f"PROFILE_MISSING {name}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise PathEscape("PROFILE_MALFORMED")
    return data


def delete_profile(root: Path, name: str) -> None:
    path = _profile_file(root, name)
    if path.is_file():
        path.unlink()
    selected = selected_name(root)
    if selected == name:
        select_profile(root, None)


def list_profiles(root: Path) -> list[str]:
    d = _profiles_dir(root)
    names = []
    for path in sorted(d.glob("*.json")):
        if path.name == SELECTED_NAME:
            continue
        names.append(path.stem)
    return names


def select_profile(root: Path, name: str | None) -> None:
    if name is None:
        path = _selected_file(root)
        if path.exists():
            path.unlink()
        return
    load_profile(root, name)
    write_json_private(_selected_file(root), {"profileName": name})


def selected_name(root: Path) -> str | None:
    path = layout(root)["profiles"] / SELECTED_NAME
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    name = str((data or {}).get("profileName") or "") or None
    return name


def selected_profile(root: Path) -> dict[str, Any] | None:
    name = selected_name(root)
    if not name:
        return None
    try:
        return load_profile(root, name)
    except PathEscape:
        return None

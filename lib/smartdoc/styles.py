from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .paths import PathEscape, assert_skill_like_name, assert_under_root, ensure_root, write_json_private

DEFAULT_STYLE = {
    "name": "notebook-default",
    "paper": "A4",
    "lineGap": 28,
    "fontSize": 20,
    "leftMargin": 92,
    "baselineJitter": 1.5,
    "rotationJitter": 1.1,
    "ink": "#1e3a8a",
    "paperTone": "#fbfaf4",
    "line": "#9db8e0",
    "margin": "#d94a4a",
    "seed": 1,
}


def _styles_dir(root: Path) -> Path:
    return ensure_root(root)["styles"]


def _style_file(root: Path, name: str) -> Path:
    assert_skill_like_name(name)
    return assert_under_root(root, _styles_dir(root) / f"{name}.json")


def create_style(root: Path, name: str, fields: dict[str, Any] | None = None) -> dict[str, Any]:
    path = _style_file(root, name)
    if path.exists():
        raise PathEscape(f"STYLE_EXISTS {name}")
    payload = dict(DEFAULT_STYLE)
    payload["name"] = name
    if fields:
        payload.update(fields)
        payload["name"] = name
    write_json_private(path, payload)
    return payload


def load_style(root: Path, name: str) -> dict[str, Any]:
    path = _style_file(root, name)
    if not path.is_file():
        raise PathEscape(f"STYLE_MISSING {name}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise PathEscape("STYLE_MALFORMED")
    return data


def delete_style(root: Path, name: str) -> None:
    path = _style_file(root, name)
    if path.is_file():
        path.unlink()


def list_styles(root: Path) -> list[str]:
    return [p.stem for p in sorted(_styles_dir(root).glob("*.json"))]


def default_style() -> dict[str, Any]:
    return dict(DEFAULT_STYLE)

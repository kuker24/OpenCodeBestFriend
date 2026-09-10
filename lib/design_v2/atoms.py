from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .importers.common import ATOMIC_ROLES, classify_atomic_role

ATOMS_SCHEMA = "impeccable.atoms.v1"
REQUIRED_ITEM_KEYS = frozenset({"id", "role", "kind", "provider"})


def map_intent_to_role(query_or_intent: str) -> str | None:
    text = (query_or_intent or "").strip()
    if not text:
        return None
    role = classify_atomic_role(text)
    if role and role in ATOMIC_ROLES:
        return role

    tokens = set(re.findall(r"[a-z0-9]+", text.lower()))
    if tokens & {"button", "btn", "ghost", "outline", "destructive", "danger", "icon", "primary"}:
        role = classify_atomic_role(text, jenis="button")
        if role and role in ATOMIC_ROLES:
            return role
    if tokens & {"modal", "dialog", "sheet", "drawer", "popover"}:
        return "overlay.modal"
    if tokens & {"sidebar", "sidenav"}:
        return "nav.sidebar-item"
    if tokens & {"tab", "tabs", "segmented"}:
        return "nav.tab"
    if tokens & {"badge", "pill", "chip"}:
        return "badge"
    if tokens & {"card", "bento"}:
        return "card"
    if tokens & {"search"}:
        return "input.search"
    if tokens & {"select", "dropdown", "combobox"}:
        return "input.select"
    if tokens & {"input", "textfield", "textarea"}:
        return "input.text"

    return None


def read_atoms(project_dir: Path | str = ".") -> dict[str, Any]:
    path = Path(project_dir).expanduser() / ".impeccable" / "atoms.json"
    if not path.is_file():
        return {"schema": ATOMS_SCHEMA, "items": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"schema": ATOMS_SCHEMA, "items": []}
    if not isinstance(data, dict) or data.get("schema") != ATOMS_SCHEMA:
        return {"schema": ATOMS_SCHEMA, "items": []}
    items = data.get("items")
    if not isinstance(items, list):
        return {"schema": ATOMS_SCHEMA, "items": []}
    valid_items = [
        item for item in items
        if isinstance(item, dict) and REQUIRED_ITEM_KEYS.issubset(item.keys())
    ]
    return {"schema": ATOMS_SCHEMA, "items": valid_items}


def write_atoms(project_dir: Path | str, payload: dict[str, Any]) -> Path:
    if not isinstance(payload, dict):
        raise ValueError("payload must be a dict")
    if payload.get("schema") != ATOMS_SCHEMA:
        raise ValueError(f"payload schema must be {ATOMS_SCHEMA!r}")
    items = payload.get("items")
    if not isinstance(items, list):
        raise ValueError("payload items must be a list")
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"item {idx} must be a dict")
        missing = REQUIRED_ITEM_KEYS - item.keys()
        if missing:
            raise ValueError(f"item {idx} missing required keys: {sorted(missing)}")

    dest_dir = Path(project_dir).expanduser() / ".impeccable"
    dest_dir.mkdir(parents=True, exist_ok=True)
    out_path = dest_dir / "atoms.json"
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out_path


def record_atom_pick(
    project_dir: Path | str,
    item: dict[str, Any],
    *,
    role: str | None = None,
) -> Path:
    item_id = str(item.get("id") or item.get("item_id") or item.get("inspect_id") or "")
    if not item_id:
        raise ValueError("item must have an id")
    resolved_role = role or item.get("role")
    if not resolved_role:
        raise ValueError("role must be provided or present in item")
    kind = str(item.get("kind") or "component")
    provider = str(item.get("provider") or (item.get("source") or {}).get("provider") or "unknown")
    local_path = item.get("local_path") or (item.get("source") or {}).get("local_path")

    record: dict[str, Any] = {
        "id": item_id,
        "role": str(resolved_role),
        "kind": kind,
        "provider": provider,
    }
    if local_path:
        record["local_path"] = str(local_path)
    canonical_id = item.get("canonical_id")
    if canonical_id:
        record["canonical_id"] = str(canonical_id)
    name = item.get("name") or item.get("direction")
    if name:
        record["name"] = str(name)

    current = read_atoms(project_dir)
    items = [existing for existing in current.get("items", []) if existing.get("role") != resolved_role]
    items.append(record)
    items.sort(key=lambda x: str(x.get("role", "")))
    return write_atoms(project_dir, {"schema": ATOMS_SCHEMA, "items": items})

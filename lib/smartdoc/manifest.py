from __future__ import annotations

from typing import Any

DONE = frozenset({"answered", "intentionally_unresolved", "impossible"})
STATUSES = frozenset({"pending", *DONE})


class ManifestError(Exception):
    code = "MANIFEST"


def empty_manifest() -> dict[str, Any]:
    return {"items": []}


def add_item(manifest: dict[str, Any], item_id: str, label: str, *, required: bool = True) -> dict[str, Any]:
    items = list(manifest.get("items") or [])
    items.append({"id": item_id, "label": label, "status": "pending", "required": required})
    out = dict(manifest)
    out["items"] = items
    return out


def set_status(manifest: dict[str, Any], item_id: str, status: str) -> dict[str, Any]:
    if status not in STATUSES:
        raise ManifestError(f"status:{status}")
    items = []
    found = False
    for item in manifest.get("items") or []:
        row = dict(item)
        if row.get("id") == item_id:
            row["status"] = status
            found = True
        items.append(row)
    if not found:
        raise ManifestError(f"missing:{item_id}")
    out = dict(manifest)
    out["items"] = items
    return out


def coverage_complete(manifest: dict[str, Any]) -> bool:
    for item in manifest.get("items") or []:
        if item.get("required", True) and item.get("status") not in DONE:
            return False
    return True


def missing_required(manifest: dict[str, Any]) -> list[str]:
    return [
        str(item.get("id"))
        for item in manifest.get("items") or []
        if item.get("required", True) and item.get("status") not in DONE
    ]

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

DESIGN_V2_RUNTIME_MISSING = "DESIGN_V2_RUNTIME_MISSING"


def _clone_engine() -> Path | None:
    here = Path(__file__).resolve()
    try:
        repo = here.parents[3]
    except IndexError:
        return None
    cand = repo / "lib" / "design_v2"
    if (cand / "__init__.py").is_file():
        return cand
    return None


def _product_engine() -> Path | None:
    raw = os.environ.get("OPENCODE_BF_ROOT")
    product = Path(raw).expanduser() if raw else Path.home() / ".local" / "share" / "opencode-bestfriend" / "product"
    cand = product / "lib" / "design_v2"
    if (cand / "__init__.py").is_file():
        return cand
    return None


def resolve_engine() -> Path:
    clone = _clone_engine()
    if clone is not None:
        return clone
    product = _product_engine()
    if product is not None:
        return product
    print(DESIGN_V2_RUNTIME_MISSING, file=sys.stderr)
    raise SystemExit(2)


def _ensure_engine_in_path() -> None:
    engine = resolve_engine()
    root = engine.parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


def map_intent_to_role(query_or_intent: str) -> str | None:
    _ensure_engine_in_path()
    from lib.design_v2.atoms import map_intent_to_role as _map

    return _map(query_or_intent)


def record_atom_pick(project_dir: Path | str, item: dict[str, Any], *, role: str | None = None) -> Path:
    _ensure_engine_in_path()
    from lib.design_v2.atoms import record_atom_pick as _record

    return _record(project_dir, item, role=role)


def read_atoms(project_dir: Path | str = ".") -> dict[str, Any]:
    _ensure_engine_in_path()
    from lib.design_v2.atoms import read_atoms as _read

    return _read(project_dir)


def write_atoms(project_dir: Path | str, payload: dict[str, Any]) -> Path:
    _ensure_engine_in_path()
    from lib.design_v2.atoms import write_atoms as _write

    return _write(project_dir, payload)


def main(argv: list[str] | None = None) -> int:
    _ensure_engine_in_path()
    from lib.design_v2.commands import add_design_cli, dispatch

    parser = argparse.ArgumentParser(
        prog="design_v2",
        description="Read-only Impeccable adapter for Design V2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    add_design_cli(parser, read_only=True)

    # Subcommand for recording atomic pick to .impeccable/atoms.json
    subparsers = next(
        (action for action in parser._actions if isinstance(action, argparse._SubParsersAction)),
        None,
    )
    if subparsers is not None:
        atom_p = subparsers.add_parser("record-atom", help="record atomic pick to .impeccable/atoms.json")
        atom_p.add_argument("--id", required=True, help="component id")
        atom_p.add_argument("--role", help="atomic role override")
        atom_p.add_argument("--provider", default="unknown", help="provider name")
        atom_p.add_argument("--local-path", help="local component path")
        atom_p.add_argument("--project", default=".", help="user project root (default: current working directory)")

    args = parser.parse_args(argv)
    action = getattr(args, "design_action", None) or getattr(args, "action", None)
    if action == "record-atom":
        item_id = args.id
        role = args.role
        provider = args.provider
        local_path = getattr(args, "local_path", None)
        # Attempt to inspect item from bank if available
        item: dict[str, Any] = {
            "id": item_id,
            "kind": "component",
            "role": role or "component",
            "provider": provider,
        }
        if local_path:
            item["local_path"] = local_path
        try:
            from lib.design_v2.inspect import inspect_item
            inspected = inspect_item(item_id)
            if inspected and isinstance(inspected, dict):
                item["role"] = role or inspected.get("role") or item["role"]
                item["provider"] = inspected.get("provider") or item["provider"]
                item["local_path"] = (inspected.get("source") or {}).get("local_path") or item.get("local_path")
                item["name"] = inspected.get("name")
        except Exception:
            pass
        out_path = record_atom_pick(args.project, item, role=role)
        print(json.dumps({"status": "ok", "path": str(out_path)}, indent=2))
        return 0

    return dispatch(args)


if __name__ == "__main__":
    raise SystemExit(main())

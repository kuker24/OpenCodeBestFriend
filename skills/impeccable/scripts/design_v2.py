#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

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


def main(argv: list[str] | None = None) -> int:
    engine = resolve_engine()
    root = engine.parent.parent
    sys.path.insert(0, str(root))
    from lib.design_v2.commands import dispatch

    parser = argparse.ArgumentParser(prog="design_v2", description="Thin Impeccable adapter for Design V2")
    parser.add_argument(
        "design_action",
        choices=[
            "status",
            "search",
            "inspect",
            "rebuild",
            "doctor",
            "ingest",
            "dedupe",
            "import",
            "sources",
            "shortlist",
        ],
    )
    parser.add_argument("target", nargs="?")
    parser.add_argument("--query")
    parser.add_argument("--kind")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--bank")
    parser.add_argument("--provider")
    parser.add_argument("--intent")
    parser.add_argument("--mode")
    parser.add_argument("--structure-only", action="store_true")
    args = parser.parse_args(argv)
    if args.design_action in {"search", "shortlist"} and not args.query:
        args.query = args.target
    return dispatch(args)


if __name__ == "__main__":
    raise SystemExit(main())

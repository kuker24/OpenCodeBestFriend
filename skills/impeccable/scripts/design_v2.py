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
    from lib.design_v2.commands import add_design_cli, dispatch

    parser = argparse.ArgumentParser(
        prog="design_v2",
        description="Read-only Impeccable adapter for Design V2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    add_design_cli(parser, read_only=True)
    args = parser.parse_args(argv)
    return dispatch(args)


if __name__ == "__main__":
    raise SystemExit(main())

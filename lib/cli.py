#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow `python3 lib/cli.py` from a clone.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.cbm import cmd_cbm_index, cmd_cbm_status  # noqa: E402
from lib.doctor import (  # noqa: E402
    cmd_chromium,
    cmd_design_bank,
    cmd_design_intelligence,
    cmd_doctor,
    cmd_mcp_status,
    cmd_security_profile,
    cmd_skills_list,
    cmd_skills_verify,
    isolation_check,
)
from lib.install import (  # noqa: E402
    cmd_install,
    cmd_restore,
    cmd_restore_list,
    cmd_serena_enable,
    cmd_uninstall,
)
from lib.integrity import cmd_verify  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="opencode-bf", description="OpenCodeBestFriend installer and doctor")
    sub = p.add_subparsers(dest="cmd", required=True)

    inst = sub.add_parser("install", help="install or update OpenCodeBestFriend")
    inst.add_argument("--dry-run", action="store_true")
    inst.add_argument("--skip-design-bank", action="store_true")
    inst.add_argument("--offline", action="store_true")
    inst.add_argument("--recover", action="store_true")

    un = sub.add_parser("uninstall", help="remove owned OpenCodeBestFriend files")
    un.add_argument("--purge-owned-design-bank", action="store_true")
    un.add_argument("--yes", action="store_true")

    sub.add_parser("update", help="re-run install from this product tree")

    rst = sub.add_parser("restore", help="restore a config backup")
    rst.add_argument("stamp", nargs="?")
    rst.add_argument("--list", action="store_true")

    doc = sub.add_parser("doctor", help="installation/config health")
    doc.add_argument("--deep", action="store_true", help="require live core MCP CONNECTED")
    doc.add_argument("--strict", action="store_true", help="treat DEGRADED/WARN as failure")

    sub.add_parser("verify", help="check installed owned files are canonical")

    cbm = sub.add_parser("cbm", help="Codebase Memory project helpers")
    cbm.add_argument("action", choices=["status", "index"])
    cbm.add_argument("path", nargs="?", default=".")

    sub.add_parser("security-profile", help="print permission recommendation (does not mutate)")

    sk = sub.add_parser("skills")
    sk.add_argument("action", choices=["list", "verify"])

    mcp = sub.add_parser("mcp")
    mcp.add_argument("action", choices=["status"])

    db = sub.add_parser("design-bank")
    db.add_argument("action", choices=["status"])

    di = sub.add_parser("design-intelligence")
    di.add_argument("action", choices=["status"])

    cr = sub.add_parser("chromium")
    cr.add_argument("action", choices=["status"])

    iso = sub.add_parser("isolation-check")
    iso.add_argument("--deep", action="store_true")

    se = sub.add_parser("serena")
    se.add_argument("action", choices=["enable"])

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    cmd = args.cmd
    if cmd == "install":
        return cmd_install(
            dry_run=args.dry_run,
            skip_design_bank=args.skip_design_bank,
            offline=args.offline,
            recover=args.recover,
        )
    if cmd == "update":
        return cmd_install()
    if cmd == "uninstall":
        return cmd_uninstall(purge_owned_bank=args.purge_owned_design_bank, yes=args.yes)
    if cmd == "restore":
        if args.list or not args.stamp:
            return cmd_restore_list()
        return cmd_restore(args.stamp)
    if cmd == "doctor":
        return cmd_doctor(deep=args.deep, strict=args.strict)
    if cmd == "verify":
        return cmd_verify()
    if cmd == "cbm":
        if args.action == "status":
            return cmd_cbm_status()
        return cmd_cbm_index(args.path)
    if cmd == "security-profile":
        return cmd_security_profile()
    if cmd == "skills":
        return cmd_skills_list() if args.action == "list" else cmd_skills_verify()
    if cmd == "mcp":
        return cmd_mcp_status()
    if cmd == "design-bank":
        return cmd_design_bank()
    if cmd == "design-intelligence":
        return cmd_design_intelligence()
    if cmd == "chromium":
        return cmd_chromium()
    if cmd == "isolation-check":
        return isolation_check(deep=args.deep)
    if cmd == "serena":
        return cmd_serena_enable()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

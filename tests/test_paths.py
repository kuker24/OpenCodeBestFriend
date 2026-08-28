#!/usr/bin/env python3
from __future__ import annotations

import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT))
from lib.install import cmd_restore, cmd_uninstall  # noqa: E402
from lib.paths import resolve_backup_stamp, tar_member_ok  # noqa: E402
from tests.support import IsolatedHome  # noqa: E402


class StampTests(IsolatedHome):
    def test_rejects_dotdot_stamp(self):
        backups = self.tmp / "backups"
        backups.mkdir()
        with self.assertRaises(SystemExit):
            resolve_backup_stamp("../something", backups)
        with self.assertRaises(SystemExit):
            resolve_backup_stamp("/tmp", backups)
        with self.assertRaises(SystemExit):
            resolve_backup_stamp("~", backups)
        with self.assertRaises(SystemExit):
            cmd_restore("../../something")

    def test_accepts_safe_stamp(self):
        backups = self.tmp / ".local" / "share" / "opencode-bestfriend" / "backups"
        dest = backups / "20260821T154439Z"
        dest.mkdir(parents=True)
        got = resolve_backup_stamp("20260821T154439Z", backups)
        self.assertEqual(got, dest.resolve())


class TarMemberTests(unittest.TestCase):
    def test_windows_and_absolute(self):
        dest = Path("/tmp/ocbf-tar-dest-test")
        dest.mkdir(exist_ok=True)
        self.addCleanup(lambda: dest.rmdir() if dest.exists() and not any(dest.iterdir()) else None)
        self.assertFalse(tar_member_ok(dest, "/etc/passwd"))
        self.assertFalse(tar_member_ok(dest, "C:/Windows/evil"))
        self.assertFalse(tar_member_ok(dest, "..\\..\\evil"))
        self.assertFalse(tar_member_ok(dest, "foo/../../etc/passwd"))
        self.assertTrue(tar_member_ok(dest, "nested/ok.txt"))


class UninstallManifestTests(IsolatedHome):
    def test_malicious_ownership_paths_are_ignored(self):
        canary = self.tmp / "evil-canary.txt"
        canary.write_text("stay\n", encoding="utf-8")
        man = self.tmp / ".config" / "opencode" / "bestfriend" / "manifests" / "ownership.json"
        man.parent.mkdir(parents=True, exist_ok=True)
        man.write_text(
            """{
  "product": "opencode-bestfriend",
  "modelInvokedSkills": ["../../../evil-canary.txt"],
  "manualSkills": ["../../tmp"],
  "ownedFiles": ["/etc/passwd", "%s"],
  "ownedMcp": []
}
"""
            % canary,
            encoding="utf-8",
        )
        self.assertEqual(cmd_uninstall(), 0)
        self.assertTrue(canary.is_file())
        self.assertEqual(canary.read_text(encoding="utf-8"), "stay\n")


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import os
import shutil
import stat
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT))
from lib import jsonc  # noqa: E402
from lib.install import cmd_install, cmd_uninstall  # noqa: E402
from lib.doctor import cmd_doctor, cmd_skills_verify, isolation_check  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.prev_home = os.environ.get("HOME")
        self.prev = {k: os.environ.get(k) for k in (
            "OPENCODE_BF_ROOT",
            "OPENCODE_BF_MOCK_OPENCODE",
            "OPENCODE_BF_TEST_CBM",
            "OPENCODE_DESIGN_BANK",
            "OPENCODE_DISABLE_CLAUDE_CODE",
        )}
        self.tmp = Path(tempfile.mkdtemp(prefix="ocbf-"))
        os.environ["HOME"] = str(self.tmp)
        os.environ["OPENCODE_BF_ROOT"] = str(ROOT)
        mock_oc = self.tmp / "mock-opencode"
        shutil.copy2(ROOT / "tests" / "fixtures" / "opencode", mock_oc)
        mock_oc.chmod(mock_oc.stat().st_mode | stat.S_IXUSR)
        mock_cbm = self.tmp / "mock-cbm"
        shutil.copy2(ROOT / "tests" / "fixtures" / "codebase-memory-mcp", mock_cbm)
        mock_cbm.chmod(mock_cbm.stat().st_mode | stat.S_IXUSR)
        os.environ["OPENCODE_BF_MOCK_OPENCODE"] = str(mock_oc)
        os.environ["OPENCODE_BF_TEST_CBM"] = str(mock_cbm)
        os.environ["OPENCODE_DESIGN_BANK"] = str(ROOT / "tests" / "fixtures" / "Design")
        os.environ["OPENCODE_DISABLE_CLAUDE_CODE"] = "1"
        claude = self.tmp / ".claude"
        claude.mkdir()
        self.sentinel = claude / "sentinel.txt"
        self.sentinel.write_text("do-not-touch\n", encoding="utf-8")
        self.sentinel_hash = sha256(self.sentinel)
        cfg = self.tmp / ".config" / "opencode"
        cfg.mkdir(parents=True)
        shutil.copy2(ROOT / "tests" / "fixtures" / "opencode.jsonc", cfg / "opencode.jsonc")

    def tearDown(self):
        if self.prev_home is None:
            os.environ.pop("HOME", None)
        else:
            os.environ["HOME"] = self.prev_home
        for k, v in self.prev.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_dry_run_no_mutation(self):
        cfg = self.tmp / ".config" / "opencode" / "opencode.jsonc"
        before = cfg.read_text(encoding="utf-8")
        rc = cmd_install(dry_run=True)
        self.assertEqual(rc, 0)
        self.assertEqual(cfg.read_text(encoding="utf-8"), before)
        self.assertFalse((self.tmp / ".config" / "opencode" / "skills").exists())
        self.assertEqual(sha256(self.sentinel), self.sentinel_hash)
        self.assertEqual(list((self.tmp / ".claude").iterdir()), [self.sentinel])

    def test_fresh_install_idempotent_uninstall(self):
        rc = cmd_install()
        self.assertEqual(rc, 0)
        self.assertEqual(sha256(self.sentinel), self.sentinel_hash)
        self.assertEqual({p.name for p in (self.tmp / ".claude").iterdir()}, {"sentinel.txt"})
        skills = list((self.tmp / ".config" / "opencode" / "skills").iterdir())
        self.assertEqual(len([p for p in skills if p.is_dir()]), 24)
        cmds = list((self.tmp / ".config" / "opencode" / "commands").glob("*.md"))
        self.assertEqual(len(cmds), 16)
        self.assertEqual(cmd_skills_verify(), 0)
        data = jsonc.load_path(self.tmp / ".config" / "opencode" / "opencode.jsonc")
        self.assertEqual(data["model"], "keep-me-model")
        self.assertIn("foreign-weather", data["mcp"])
        self.assertIn("codebase-memory-mcp", data["mcp"])
        self.assertNotIn("compaction", data)
        self.assertIn("OPENCODEBESTFRIEND:BEGIN", (self.tmp / ".bashrc").read_text(encoding="utf-8"))
        self.assertEqual(isolation_check(), 0)
        self.assertEqual(cmd_doctor(), 0)

        rc2 = cmd_install()
        self.assertEqual(rc2, 0)
        self.assertEqual(len([p for p in (self.tmp / ".config" / "opencode" / "skills").iterdir() if p.is_dir()]), 24)
        self.assertEqual(len(list((self.tmp / ".config" / "opencode" / "commands").glob("*.md"))), 16)
        bashrc = (self.tmp / ".bashrc").read_text(encoding="utf-8")
        self.assertEqual(bashrc.count("OPENCODEBESTFRIEND:BEGIN"), 1)
        data2 = jsonc.load_path(self.tmp / ".config" / "opencode" / "opencode.jsonc")
        self.assertEqual(data2["mcp"]["foreign-weather"]["url"], "https://example.invalid/mcp")
        self.assertEqual(data2["provider"]["example"]["options"]["note"], "user-owned-provider")

        rc3 = cmd_uninstall()
        self.assertEqual(rc3, 0)
        self.assertFalse((self.tmp / ".config" / "opencode" / "bestfriend").exists())
        data3 = jsonc.load_path(self.tmp / ".config" / "opencode" / "opencode.jsonc")
        self.assertIn("foreign-weather", data3["mcp"])
        self.assertNotIn("codebase-memory-mcp", data3["mcp"])
        self.assertEqual(data3["model"], "keep-me-model")
        self.assertEqual(sha256(self.sentinel), self.sentinel_hash)
        self.assertNotIn("OPENCODEBESTFRIEND:BEGIN", (self.tmp / ".bashrc").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

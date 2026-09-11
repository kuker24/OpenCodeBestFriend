#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import os
import shutil
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT))
from lib import jsonc  # noqa: E402
from lib.install import (  # noqa: E402
    backup_relevant,
    cmd_install,
    cmd_restore,
    cmd_serena_enable,
    cmd_stitch_disable,
    cmd_stitch_enable,
    cmd_uninstall,
)
from lib.doctor import cmd_doctor, cmd_skills_verify, isolation_check  # noqa: E402
from lib.design_v2.bootstrap import BootstrapError  # noqa: E402


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
            "OPENCODE_SMARTDOC",
            "OPENCODE_DISABLE_CLAUDE_CODE",
            "PATH",
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

    def test_normal_install_never_downloads_design_bank(self):
        os.environ.pop("OPENCODE_DESIGN_BANK", None)
        with patch("lib.install.urllib.request.urlretrieve", side_effect=AssertionError("unexpected network download")):
            self.assertEqual(cmd_install(), 0)
        self.assertTrue((self.tmp / ".local" / "bin" / "opencode-bf").is_file())
        self.assertFalse((self.tmp / "Design").exists())

    def test_with_design_bank_runs_optional_post_install_bootstrap(self):
        payload = {"status": "ok", "target": str(self.tmp / "Design")}
        with patch("lib.design_v2.bootstrap.bootstrap_design_bank", return_value=payload) as mocked:
            self.assertEqual(cmd_install(with_design_bank=True), 0)
        mocked.assert_called_once()
        self.assertTrue((self.tmp / ".local" / "bin" / "opencode-bf").is_file())

    def test_bootstrap_failure_preserves_successful_core_install(self):
        failure = BootstrapError("ARCHIVE_DOWNLOADED", "network unavailable", code="DOWNLOAD_FAILED")
        with patch("lib.design_v2.bootstrap.bootstrap_design_bank", side_effect=failure):
            self.assertEqual(cmd_install(with_design_bank=True), 1)
        self.assertTrue((self.tmp / ".local" / "bin" / "opencode-bf").is_file())
        self.assertTrue((self.tmp / ".local" / "share" / "opencode-bestfriend" / "product").is_dir())

    def test_fresh_install_idempotent_uninstall(self):
        rc = cmd_install()
        self.assertEqual(rc, 0)
        self.assertEqual(sha256(self.sentinel), self.sentinel_hash)
        self.assertEqual({p.name for p in (self.tmp / ".claude").iterdir()}, {"sentinel.txt"})
        skills = list((self.tmp / ".config" / "opencode" / "skills").iterdir())
        self.assertEqual(len([p for p in skills if p.is_dir()]), 46)
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
        self.assertEqual(len([p for p in (self.tmp / ".config" / "opencode" / "skills").iterdir() if p.is_dir()]), 46)
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

    def test_uninstall_preserves_user_design_and_design_v2(self):
        self.assertEqual(cmd_install(), 0)
        design = self.tmp / "Design"
        design_v2 = self.tmp / "DesignV2"
        smartdoc = self.tmp / "SmartDoc"
        design.mkdir()
        design_v2.mkdir()
        smartdoc.mkdir()
        (design / "sentinel.txt").write_text("keep\n", encoding="utf-8")
        (design_v2 / "sentinel.txt").write_text("keep\n", encoding="utf-8")
        (smartdoc / "sentinel.txt").write_text("keep\n", encoding="utf-8")
        self.assertEqual(cmd_uninstall(), 0)
        self.assertEqual((design / "sentinel.txt").read_text(encoding="utf-8"), "keep\n")
        self.assertEqual((design_v2 / "sentinel.txt").read_text(encoding="utf-8"), "keep\n")
        self.assertEqual((smartdoc / "sentinel.txt").read_text(encoding="utf-8"), "keep\n")

    def test_agents_marker_merge_and_uninstall(self):
        agents = self.tmp / ".config" / "opencode" / "AGENTS.md"
        agents.write_text("USER RULES stay here\n", encoding="utf-8")
        self.assertEqual(cmd_install(), 0)
        text = agents.read_text(encoding="utf-8")
        self.assertIn("USER RULES stay here", text)
        self.assertIn("OPENCODEBESTFRIEND:BEGIN", text)
        self.assertEqual(cmd_uninstall(), 0)
        leftover = agents.read_text(encoding="utf-8")
        self.assertIn("USER RULES stay here", leftover)
        self.assertNotIn("OPENCODEBESTFRIEND:BEGIN", leftover)

    def test_foreign_command_collision(self):
        dest = self.tmp / ".config" / "opencode" / "commands"
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "architect.md").write_text("# my architect\n", encoding="utf-8")
        with self.assertRaises(SystemExit):
            cmd_install()
        self.assertEqual((dest / "architect.md").read_text(encoding="utf-8"), "# my architect\n")

    def test_jsonc_comments_survive_install(self):
        cfg = self.tmp / ".config" / "opencode" / "opencode.jsonc"
        cfg.write_text(
            """{
  // keep this comment
  "model": "keep-me-model",
  "mcp": {
    "foreign-weather": {
      "type": "remote",
      "url": "https://example.invalid/mcp",
      "enabled": true
    }
  }
}
""",
            encoding="utf-8",
        )
        self.assertEqual(cmd_install(), 0)
        text = cfg.read_text(encoding="utf-8")
        self.assertIn("keep this comment", text)
        self.assertIn("foreign-weather", text)
        self.assertIn("codebase-memory-mcp", text)

    def test_rejects_opencode_1_19(self):
        mock = self.tmp / "mock-opencode"
        mock.write_text("#!/bin/sh\necho 1.19.0\n", encoding="utf-8")
        mock.chmod(mock.stat().st_mode | stat.S_IXUSR)
        with self.assertRaises(SystemExit):
            cmd_install(dry_run=True)

    def test_restore_deletes_absent_preinstall(self):
        cfg = self.tmp / ".config" / "opencode" / "opencode.jsonc"
        cfg.unlink()
        stamp = "testrb"
        backup_relevant(stamp, {"model": []})
        cfg.write_text("{}\n", encoding="utf-8")
        agents = self.tmp / ".config" / "opencode" / "AGENTS.md"
        agents.write_text("created by installer\n", encoding="utf-8")
        commands = self.tmp / ".config" / "opencode" / "commands"
        commands.mkdir()
        (commands / "architect.md").write_text("x\n", encoding="utf-8")
        bashrc = self.tmp / ".bashrc"
        bashrc.write_text("# OPENCODEBESTFRIEND:BEGIN\n", encoding="utf-8")
        self.assertEqual(cmd_restore(stamp), 0)
        self.assertFalse(cfg.exists())
        self.assertFalse(agents.exists())
        self.assertFalse(commands.exists())
        self.assertFalse(bashrc.exists())

    def test_doctor_counts_owned_agents_block(self):
        agents = self.tmp / ".config" / "opencode" / "AGENTS.md"
        agents.write_text(("USER RULE line\n" * 180), encoding="utf-8")
        self.assertEqual(cmd_install(), 0)
        self.assertEqual(cmd_doctor(), 0)

    def test_foreign_helper_collision(self):
        dest = self.tmp / ".local" / "bin"
        dest.mkdir(parents=True, exist_ok=True)
        helper = dest / "opencode-bf"
        helper.write_text("#!/bin/sh\necho foreign\n", encoding="utf-8")
        helper.chmod(helper.stat().st_mode | stat.S_IXUSR)
        cfg = self.tmp / ".config" / "opencode" / "opencode.jsonc"
        before = cfg.read_text(encoding="utf-8")
        with self.assertRaises(SystemExit):
            cmd_install()
        self.assertEqual(helper.read_text(encoding="utf-8"), "#!/bin/sh\necho foreign\n")
        self.assertEqual(cfg.read_text(encoding="utf-8"), before)
        self.assertFalse((self.tmp / ".config" / "opencode" / "skills").exists())
        self.assertFalse((self.tmp / ".config" / "opencode" / "commands").exists())
        self.assertFalse((self.tmp / ".config" / "opencode" / "AGENTS.md").exists())

    def _fake_serena(self) -> None:
        bindir = self.tmp / "pathbin"
        bindir.mkdir(parents=True, exist_ok=True)
        serena = bindir / "serena"
        serena.write_text("#!/bin/sh\necho serena\n", encoding="utf-8")
        serena.chmod(serena.stat().st_mode | stat.S_IXUSR)
        os.environ["PATH"] = f"{bindir}:{os.environ.get('PATH', '')}"

    def test_serena_enable_invalid_config_fail_closed(self):
        self._fake_serena()
        cfg = self.tmp / ".config" / "opencode" / "opencode.jsonc"
        cfg.write_text("{ not json", encoding="utf-8")
        with self.assertRaises(SystemExit):
            cmd_serena_enable()
        self.assertEqual(cfg.read_text(encoding="utf-8"), "{ not json")

    def test_serena_enable_preserves_jsonc_comments(self):
        self._fake_serena()
        cfg = self.tmp / ".config" / "opencode" / "opencode.jsonc"
        cfg.write_text(
            """{
  // provider utama saya
  "model": "keep-me-model",
  "provider": {"example": {"options": {"note": "user-owned-provider"}}},
  "mcp": {
    "foreign-weather": {
      "type": "remote",
      "url": "https://example.invalid/mcp",
      "enabled": true
    }
  }
}
""",
            encoding="utf-8",
        )
        self.assertEqual(cmd_serena_enable(), 0)
        text = cfg.read_text(encoding="utf-8")
        self.assertIn("provider utama saya", text)
        data = jsonc.loads(text)
        self.assertEqual(data["model"], "keep-me-model")
        self.assertEqual(data["provider"]["example"]["options"]["note"], "user-owned-provider")
        self.assertIn("foreign-weather", data["mcp"])
        self.assertIn("serena", data["mcp"])
        self.assertEqual(cmd_serena_enable(), 0)
        self.assertEqual(cfg.read_text(encoding="utf-8"), text)

    def test_stitch_enable_requires_env_or_oauth(self):
        os.environ.pop("STITCH_API_KEY", None)
        with self.assertRaises(SystemExit):
            cmd_stitch_enable(oauth=False)

    def test_stitch_enable_does_not_overwrite_existing_entry(self):
        cfg = self.tmp / ".config" / "opencode" / "opencode.jsonc"
        cfg.parent.mkdir(parents=True, exist_ok=True)
        original = (
            "{\n"
            '  "mcp": {\n'
            '    "stitch": {\n'
            '      "type": "remote",\n'
            '      "url": "https://stitch.googleapis.com/mcp",\n'
            '      "enabled": true,\n'
            '      "headers": {"Authorization": "{env:MY_OWN_TOKEN}"}\n'
            "    }\n"
            "  }\n"
            "}\n"
        )
        cfg.write_text(original, encoding="utf-8")
        os.environ["STITCH_API_KEY"] = "mock_secret_key_12345"
        try:
            self.assertEqual(cmd_stitch_enable(oauth=False), 0)
        finally:
            os.environ.pop("STITCH_API_KEY", None)
        self.assertEqual(cfg.read_text(encoding="utf-8"), original)

    def test_stitch_enable_null_mcp_fails_closed(self):
        cfg = self.tmp / ".config" / "opencode" / "opencode.jsonc"
        cfg.parent.mkdir(parents=True, exist_ok=True)
        original = '{\n  "mcp": null\n}\n'
        cfg.write_text(original, encoding="utf-8")
        self.assertEqual(cmd_stitch_enable(oauth=True), 0)
        data = jsonc.loads(cfg.read_text(encoding="utf-8"))
        self.assertEqual(data["mcp"]["stitch"]["url"], "https://stitch.googleapis.com/mcp")

    def test_stitch_enable_with_env_key(self):
        os.environ["STITCH_API_KEY"] = "mock_secret_key_12345"
        try:
            cfg = self.tmp / ".config" / "opencode" / "opencode.jsonc"
            cfg.parent.mkdir(parents=True, exist_ok=True)
            cfg.write_text(
                """{
  // existing config
  "model": "keep-me-model",
  "mcp": {
    "foreign-weather": {
      "type": "remote",
      "url": "https://example.invalid/mcp",
      "enabled": true
    }
  }
}
""",
                encoding="utf-8",
            )
            self.assertEqual(cmd_stitch_enable(oauth=False), 0)
            text = cfg.read_text(encoding="utf-8")
            self.assertIn("// existing config", text)
            # Secret key value must NEVER be written to the file
            self.assertNotIn("mock_secret_key_12345", text)
            self.assertIn("{env:STITCH_API_KEY}", text)
            data = jsonc.loads(text)
            self.assertEqual(data["model"], "keep-me-model")
            self.assertIn("foreign-weather", data["mcp"])
            self.assertIn("stitch", data["mcp"])
            stitch_spec = data["mcp"]["stitch"]
            self.assertEqual(stitch_spec["type"], "remote")
            self.assertEqual(stitch_spec["url"], "https://stitch.googleapis.com/mcp")
            self.assertTrue(stitch_spec["enabled"])
            self.assertEqual(stitch_spec["headers"]["X-Goog-Api-Key"], "{env:STITCH_API_KEY}")
        finally:
            os.environ.pop("STITCH_API_KEY", None)

    def test_stitch_enable_oauth(self):
        cfg = self.tmp / ".config" / "opencode" / "opencode.jsonc"
        cfg.parent.mkdir(parents=True, exist_ok=True)
        cfg.write_text("{\n  \"mcp\": {}\n}\n", encoding="utf-8")
        self.assertEqual(cmd_stitch_enable(oauth=True), 0)
        text = cfg.read_text(encoding="utf-8")
        data = jsonc.loads(text)
        self.assertIn("stitch", data["mcp"])
        stitch_spec = data["mcp"]["stitch"]
        self.assertEqual(stitch_spec["type"], "remote")
        self.assertEqual(stitch_spec["url"], "https://stitch.googleapis.com/mcp")
        self.assertTrue(stitch_spec["enabled"])
        self.assertNotIn("headers", stitch_spec)

    def test_stitch_disable_removes_only_stitch(self):
        cfg = self.tmp / ".config" / "opencode" / "opencode.jsonc"
        cfg.parent.mkdir(parents=True, exist_ok=True)
        cfg.write_text(
            """{
  // penting: keep this comment
  "model": "keep-me-model",
  "provider": {"example": {"options": {"note": "user-owned-provider"}}},
  "mcp": {
    "foreign-weather": {
      "type": "remote",
      "url": "https://example.invalid/mcp",
      "enabled": true
    },
    "stitch": {
      "type": "remote",
      "url": "https://stitch.googleapis.com/mcp",
      "enabled": true
    }
  }
}
""",
            encoding="utf-8",
        )
        self.assertEqual(cmd_stitch_disable(), 0)
        text = cfg.read_text(encoding="utf-8")
        self.assertIn("penting: keep this comment", text)
        data = jsonc.loads(text)
        self.assertEqual(data["model"], "keep-me-model")
        self.assertEqual(data["provider"]["example"]["options"]["note"], "user-owned-provider")
        self.assertIn("foreign-weather", data["mcp"])
        self.assertNotIn("stitch", data["mcp"])

    def test_stitch_enable_invalid_config_fail_closed(self):
        cfg = self.tmp / ".config" / "opencode" / "opencode.jsonc"
        cfg.parent.mkdir(parents=True, exist_ok=True)
        cfg.write_text("{ not valid json", encoding="utf-8")
        with self.assertRaises(SystemExit):
            cmd_stitch_enable(oauth=True)
        self.assertEqual(cfg.read_text(encoding="utf-8"), "{ not valid json")

    def test_stitch_disable_invalid_config_fail_closed(self):
        cfg = self.tmp / ".config" / "opencode" / "opencode.jsonc"
        cfg.parent.mkdir(parents=True, exist_ok=True)
        cfg.write_text("{ not valid json", encoding="utf-8")
        with self.assertRaises(SystemExit):
            cmd_stitch_disable()
        self.assertEqual(cfg.read_text(encoding="utf-8"), "{ not valid json")

    def test_restore_prior_product_tree(self):
        product = self.tmp / ".local" / "share" / "opencode-bestfriend" / "product"
        product.mkdir(parents=True)
        (product / "VERSION").write_text("1.0.1\n", encoding="utf-8")
        stamp = "upg"
        backup_relevant(stamp, {"model": []})
        (product / "VERSION").write_text("1.0.2\n", encoding="utf-8")
        self.assertEqual(cmd_restore(stamp), 0)
        self.assertEqual((product / "VERSION").read_text(encoding="utf-8"), "1.0.1\n")


if __name__ == "__main__":
    unittest.main()


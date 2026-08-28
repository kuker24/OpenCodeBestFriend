#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import io
import os
import stat
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT))
from lib import jsonc  # noqa: E402
from lib.common import product_version  # noqa: E402
from lib.doctor import cmd_doctor  # noqa: E402
from lib.identity import EXPECTED_PRODUCT, EXPECTED_REPO  # noqa: E402
from lib.install import cmd_install, cmd_recover  # noqa: E402
from lib.integrity import cmd_verify  # noqa: E402
from tests.support import IsolatedHome  # noqa: E402


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MigrationTests(IsolatedHome):
    def _plant_legacy(self) -> dict[str, str]:
        cfg = self.tmp / ".config" / "opencode"
        bf = cfg / "bestfriend"
        (bf / "manifests").mkdir(parents=True)
        (bf / "rules").mkdir(parents=True)
        (cfg / "commands").mkdir(parents=True)
        (self.tmp / ".local" / "bin").mkdir(parents=True)
        (bf / "manifests" / "ownership.json").write_text(
            """{
  "product": "opencode-bestfriend",
  "sourceRepository": "https://github.com/kuker24/ClaudeBestFriend",
  "sourceVersion": "1.4.2-claude.1",
  "ownedMcp": ["codebase-memory-mcp", "context7", "shadcn"]
}
""",
            encoding="utf-8",
        )
        (cfg / "AGENTS.md").write_text(
            "<!-- OPENCODEBESTFRIEND:BEGIN -->\n# old router\n<!-- OPENCODEBESTFRIEND:END -->\n",
            encoding="utf-8",
        )
        (bf / "rules" / "00-routing.md").write_text(
            "# Claude Code specialist routing (opencode-bestfriend)\n",
            encoding="utf-8",
        )
        helper = self.tmp / ".local" / "bin" / "opencode-bf"
        helper.write_text(
            "#!/usr/bin/env bash\n"
            "ROOT=\"${OPENCODE_BF_INSTALLER:-$HOME/.local/share/opencode-bestfriend/components/installer}\"\n"
            "exec python3 \"$ROOT/opencode_bf.py\" \"$@\"\n",
            encoding="utf-8",
        )
        helper.chmod(helper.stat().st_mode | stat.S_IXUSR)
        (self.tmp / ".local" / "share" / "opencode-bestfriend" / "source" / "ClaudeBestFriend").mkdir(parents=True)
        cfgj = cfg / "opencode.jsonc"
        return {
            "config": _sha(cfgj),
            "agents": _sha(cfg / "AGENTS.md"),
            "helper": _sha(helper),
            "sentinel": _sha(self.sentinel),
        }

    def test_migrate_claudebestfriend_1_4_2_to_ocbf(self):
        self._plant_legacy()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_install()
        self.assertEqual(rc, 0, buf.getvalue())
        self.assertIn("MIGRATION_DETECTED", buf.getvalue())
        man = jsonc.load_path(self.tmp / ".config" / "opencode" / "bestfriend" / "manifests" / "ownership.json")
        self.assertEqual(man["product"], EXPECTED_PRODUCT)
        self.assertEqual(man["productVersion"], product_version())
        self.assertEqual(man["sourceRepository"], EXPECTED_REPO)
        self.assertEqual(man["migration"]["fromProduct"], "ClaudeBestFriend")
        agents = (self.tmp / ".config" / "opencode" / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("USED", agents)
        self.assertIn("CONSIDERED_NOT_USED", agents)
        self.assertIn("MANUAL_NOT_INVOKED", agents)
        routing = (self.tmp / ".config" / "opencode" / "bestfriend" / "rules" / "00-routing.md").read_text(
            encoding="utf-8"
        )
        self.assertTrue(routing.startswith("# OpenCode specialist routing (opencode-bestfriend)"))
        data = jsonc.load_path(self.tmp / ".config" / "opencode" / "opencode.jsonc")
        self.assertEqual(data["model"], "keep-me-model")
        self.assertIn("foreign-weather", data["mcp"])
        self.assertEqual(data["provider"]["example"]["options"]["note"], "user-owned-provider")
        self.assertEqual(_sha(self.sentinel), hashlib.sha256(b"do-not-touch\n").hexdigest())
        helper = (self.tmp / ".local" / "bin" / "opencode-bf").read_text(encoding="utf-8")
        self.assertIn("lib/cli.py", helper)
        self.assertNotIn("opencode_bf.py", helper)
        skills = list((self.tmp / ".config" / "opencode" / "skills").iterdir())
        self.assertEqual(len([p for p in skills if p.is_dir()]), 24)
        with redirect_stdout(io.StringIO()):
            self.assertEqual(cmd_verify(), 0)
            self.assertEqual(cmd_doctor(), 0)

    def test_failed_migration_restores_legacy_exactly(self):
        before = self._plant_legacy()
        os.environ["OPENCODE_BF_FORCE_VERIFY_FAIL"] = "1"
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_install()
        self.assertEqual(rc, 1, buf.getvalue())
        with redirect_stdout(io.StringIO()):
            self.assertEqual(cmd_recover(), 0)
        cfg = self.tmp / ".config" / "opencode"
        self.assertEqual(_sha(cfg / "opencode.jsonc"), before["config"])
        self.assertEqual(_sha(cfg / "AGENTS.md"), before["agents"])
        self.assertEqual(_sha(self.tmp / ".local" / "bin" / "opencode-bf"), before["helper"])
        self.assertEqual(_sha(self.sentinel), before["sentinel"])
        man = jsonc.load_path(cfg / "bestfriend" / "manifests" / "ownership.json")
        self.assertEqual(man.get("sourceVersion"), "1.4.2-claude.1")
        self.assertNotIn("productVersion", man)

    def test_upgrade_1_0_4_to_current(self):
        self.assertEqual(cmd_install(), 0)
        man_path = self.tmp / ".config" / "opencode" / "bestfriend" / "manifests" / "ownership.json"
        man = jsonc.load_path(man_path)
        man["productVersion"] = "1.0.4"
        man_path.write_text(__import__("json").dumps(man, indent=2) + "\n", encoding="utf-8")
        agents = self.tmp / ".config" / "opencode" / "AGENTS.md"
        agents.write_text(
            "<!-- OPENCODEBESTFRIEND:BEGIN -->\n# stale\n<!-- OPENCODEBESTFRIEND:END -->\n",
            encoding="utf-8",
        )
        with redirect_stdout(io.StringIO()):
            self.assertEqual(cmd_doctor(), 1)
            self.assertEqual(cmd_install(), 0)
            self.assertEqual(cmd_doctor(), 0)
            self.assertEqual(cmd_verify(), 0)
        man2 = jsonc.load_path(man_path)
        self.assertEqual(man2["productVersion"], product_version())
        self.assertIn("USED", agents.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT))
import io
import os
import shutil
from contextlib import redirect_stdout

from lib.doctor import cmd_doctor, owned_agents_block, parse_mcp_list  # noqa: E402
from lib.install import cmd_install  # noqa: E402
from lib.integrity import cmd_verify  # noqa: E402
from tests.support import IsolatedHome  # noqa: E402


class McpListParserTests(unittest.TestCase):
    def test_per_server_connected_vs_disconnected(self):
        text = """
codebase-memory-mcp connected
context7 disconnected
shadcn connected
"""
        out = parse_mcp_list(text)
        self.assertEqual(out["codebase-memory-mcp"], "CONNECTED")
        self.assertEqual(out["context7"], "DISCONNECTED")
        self.assertEqual(out["shadcn"], "CONNECTED")

    def test_disconnected_is_not_connected_substring(self):
        text = "context7 disconnected\n"
        out = parse_mcp_list(text)
        self.assertEqual(out["context7"], "DISCONNECTED")
        self.assertEqual(out["codebase-memory-mcp"], "NOT_CHECKED")
        self.assertEqual(out["shadcn"], "NOT_CHECKED")

    def test_skips_ambiguous_multi_name_line(self):
        text = "codebase-memory-mcp connected context7 disconnected\n"
        out = parse_mcp_list(text)
        self.assertEqual(out["codebase-memory-mcp"], "NOT_CHECKED")
        self.assertEqual(out["context7"], "NOT_CHECKED")

    def test_strips_ansi_and_parses_connected(self):
        text = "\x1b[0m\n●  ✓ codebase-memory-mcp \x1b[90mconnected\n"
        out = parse_mcp_list(text)
        self.assertEqual(out["codebase-memory-mcp"], "CONNECTED")

    def test_path_line_does_not_downgrade_connected(self):
        text = """
●  ✓ codebase-memory-mcp connected
│      /home/u/.local/share/opencode-bestfriend/components/codebase-memory/bin/codebase-memory-mcp
●  ✓ context7 connected
│      https://mcp.context7.com/mcp
●  ✓ shadcn connected
│      npx -y shadcn@4.18.0 mcp
"""
        out = parse_mcp_list(text)
        self.assertEqual(out["codebase-memory-mcp"], "CONNECTED")
        self.assertEqual(out["context7"], "CONNECTED")
        self.assertEqual(out["shadcn"], "CONNECTED")


class AgentsBlockTests(unittest.TestCase):
    def test_owned_block_ignores_foreign_text(self):
        text = ("USER\n" * 200) + "<!-- OPENCODEBESTFRIEND:BEGIN -->\nrouter\n<!-- OPENCODEBESTFRIEND:END -->\n"
        block = owned_agents_block(text)
        self.assertIsNotNone(block)
        self.assertLessEqual(block.count("\n"), 5)
        self.assertGreater(text.count("\n"), 120)


class DoctorDeepTests(IsolatedHome):
    def _install(self):
        self.assertEqual(cmd_install(), 0)

    def test_deep_all_connected_exits_0(self):
        self._install()
        self.write_mcp_list(
            "codebase-memory-mcp connected\ncontext7 connected\nshadcn connected\n"
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_doctor(deep=True)
        self.assertEqual(rc, 0, buf.getvalue())
        self.assertIn("CONNECTED", buf.getvalue())

    def test_deep_one_disconnected_exits_1(self):
        self._install()
        self.write_mcp_list(
            "codebase-memory-mcp connected\ncontext7 disconnected\nshadcn connected\n"
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_doctor(deep=True)
        self.assertEqual(rc, 1, buf.getvalue())
        self.assertIn("DISCONNECTED", buf.getvalue())

    def test_deep_not_checked_exits_1(self):
        self._install()
        self.write_mcp_list("codebase-memory-mcp connected\n")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_doctor(deep=True)
        self.assertEqual(rc, 1, buf.getvalue())

    def test_deep_empty_list_exits_1(self):
        self._install()
        os.environ.pop("OPENCODE_BF_MOCK_MCP_LIST", None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_doctor(deep=True)
        self.assertEqual(rc, 1, buf.getvalue())

    def test_deep_command_failure_exits_1(self):
        self._install()
        self.write_mcp_list("codebase-memory-mcp connected\ncontext7 connected\nshadcn connected\n")
        os.environ["OPENCODE_BF_MOCK_MCP_LIST_RC"] = "1"
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_doctor(deep=True)
        self.assertEqual(rc, 1, buf.getvalue())

    def test_non_deep_does_not_claim_connected(self):
        self._install()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_doctor(deep=False)
        self.assertEqual(rc, 0, buf.getvalue())
        self.assertNotIn("PASS                   mcp:context7                 CONNECTED", buf.getvalue())
        self.assertIn("CONFIGURED", buf.getvalue())

    def test_stale_agents_detected(self):
        self._install()
        agents = self.tmp / ".config" / "opencode" / "AGENTS.md"
        text = agents.read_text(encoding="utf-8")
        text = text.replace("USED", "NOPE").replace("CONSIDERED_NOT_USED", "X").replace("MANUAL_NOT_INVOKED", "Y")
        agents.write_text(text, encoding="utf-8")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_doctor()
        self.assertEqual(rc, 1, buf.getvalue())
        self.assertIn("STALE", buf.getvalue())
        with redirect_stdout(io.StringIO()):
            self.assertEqual(cmd_verify(), 1)

    def test_installed_design_v2_runtime_drift_detected(self):
        self._install()
        runtime = (
            self.tmp
            / ".local"
            / "share"
            / "opencode-bestfriend"
            / "product"
            / "lib"
            / "design_v2"
            / "search.py"
        )
        runtime.write_text(runtime.read_text(encoding="utf-8") + "\n# drift\n", encoding="utf-8")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_verify()
        self.assertEqual(rc, 1, buf.getvalue())
        self.assertIn("DRIFT", buf.getvalue())
        self.assertIn("product/lib/design_v2/search.py", buf.getvalue())

    def test_missing_installed_design_v2_runtime_detected(self):
        self._install()
        runtime = (
            self.tmp
            / ".local"
            / "share"
            / "opencode-bestfriend"
            / "product"
            / "lib"
            / "design_v2"
            / "search.py"
        )
        runtime.unlink()
        os.environ["OPENCODE_BF_ROOT"] = str(
            self.tmp / ".local" / "share" / "opencode-bestfriend" / "product"
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_verify()
        self.assertEqual(rc, 1, buf.getvalue())
        self.assertIn("MISSING", buf.getvalue())
        self.assertIn("product/lib/design_v2/search.py", buf.getvalue())

    def test_stale_routing_detected(self):
        self._install()
        routing = self.tmp / ".config" / "opencode" / "bestfriend" / "rules" / "00-routing.md"
        routing.write_text("# Claude Code specialist routing (opencode-bestfriend)\n", encoding="utf-8")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_doctor()
        self.assertEqual(rc, 1, buf.getvalue())
        self.assertIn("STALE", buf.getvalue())

    def test_context_guard_not_pass(self):
        self._install()
        buf = io.StringIO()
        with redirect_stdout(buf):
            cmd_doctor()
        out = buf.getvalue()
        self.assertIn("NOT_APPLICABLE", out)
        self.assertIn("NOT_PORTED_BY_DESIGN", out)
        self.assertNotIn("PASS                   Context Guard", out)

    def test_permission_wildcard_degraded_strict_fails(self):
        cfg = self.tmp / ".config" / "opencode" / "opencode.jsonc"
        cfg.write_text(
            """{
  "permission": { "*": "allow" },
  "mcp": {}
}
""",
            encoding="utf-8",
        )
        self._install()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_doctor()
        self.assertEqual(rc, 0, buf.getvalue())
        self.assertIn("DEGRADED_SECURITY", buf.getvalue())
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_doctor(strict=True)
        self.assertEqual(rc, 1, buf.getvalue())

    def test_shadcn_requires_node_npx(self):
        self._install()
        empty = self.tmp / "empty-bin"
        empty.mkdir()
        py = shutil.which("python3")
        self.assertIsNotNone(py)
        os.symlink(py, empty / "python3")
        os.environ["PATH"] = str(empty)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_doctor()
        os.environ["PATH"] = self.prev["PATH"] or ""
        self.assertEqual(rc, 1, buf.getvalue())
        self.assertTrue("npx" in buf.getvalue() or "node" in buf.getvalue())


if __name__ == "__main__":
    unittest.main()

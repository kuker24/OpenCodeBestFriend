from __future__ import annotations

import os
import shutil
import stat
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class IsolatedHome(unittest.TestCase):
    def setUp(self):
        self.prev_home = os.environ.get("HOME")
        self.prev = {
            k: os.environ.get(k)
            for k in (
                "OPENCODE_BF_ROOT",
                "OPENCODE_BF_MOCK_OPENCODE",
                "OPENCODE_BF_TEST_CBM",
                "OPENCODE_DESIGN_BANK",
                "OPENCODE_DISABLE_CLAUDE_CODE",
                "OPENCODE_BF_MOCK_MCP_LIST",
                "OPENCODE_BF_MOCK_MCP_LIST_RC",
                "OPENCODE_BF_FORCE_VERIFY_FAIL",
                "PATH",
            )
        }
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

    def write_mcp_list(self, text: str) -> Path:
        path = self.tmp / "mcp-list.txt"
        path.write_text(text, encoding="utf-8")
        os.environ["OPENCODE_BF_MOCK_MCP_LIST"] = str(path)
        return path

#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTIVE = (
    "~/.claude/",
    "$HOME/.claude/",
    "claude-gbf",
    "CLAUDE_CODE_",
    "CLAUDE_DESIGN_BANK",
    "grokbestfriend-claude",
    "claude mcp",
)
SKIP_NAMES = {"THIRD_PARTY_NOTICES.md", "provenance.json", "sources.json", "README.md", "CHANGELOG.md", "security.md"}
SKIP_PARTS = {"docs", "licenses", ".git", "tests"}
SKIP_FILES = {("lib", "install.py"), ("lib", "doctor.py")}


class IsolationTests(unittest.TestCase):
    def test_no_active_claude_runtime(self):
        hits = []
        for path in ROOT.rglob("*"):
            if not path.is_file():
                continue
            if any(p in SKIP_PARTS for p in path.parts):
                continue
            if path.name in SKIP_NAMES:
                continue
            if tuple(path.parts[-2:]) in SKIP_FILES:
                continue
            if path.suffix not in {".md", ".json", ".jsonc", ".mjs", ".js", ".py", ".sh", ""}:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for pat in ACTIVE:
                if pat in text:
                    hits.append(f"{path.relative_to(ROOT)}: {pat}")
                    break
        self.assertEqual(hits, [])

    def test_no_personal_path(self):
        hits = []
        for path in ROOT.rglob("*"):
            if not path.is_file() or ".git" in path.parts:
                continue
            if path.suffix not in {".md", ".json", ".jsonc", ".mjs", ".js", ".py", ".sh", ".yml", ""}:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            needle = "/" + "home" + "/" + "fahmiagent"
            if needle in text:
                hits.append(str(path.relative_to(ROOT)))
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()

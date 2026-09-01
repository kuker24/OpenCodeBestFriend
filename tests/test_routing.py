#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.agents = (ROOT / "templates" / "AGENTS.md").read_text(encoding="utf-8")
        self.routing = (ROOT / "rules" / "00-routing.md").read_text(encoding="utf-8")

    def test_thin_router(self):
        self.assertIn("OPENCODEBESTFRIEND:BEGIN", self.agents)
        self.assertNotIn("@~/", self.agents)
        self.assertNotIn("Context Guard", self.agents)
        self.assertLessEqual(self.agents.count("\n"), 120)
        self.assertIn("USED", self.agents)
        self.assertIn("CONSIDERED_NOT_USED", self.agents)
        self.assertIn("MANUAL_NOT_INVOKED", self.agents)
        self.assertTrue(self.routing.startswith("# OpenCode specialist routing (opencode-bestfriend)"))

    def test_mappings(self):
        blob = self.agents + "\n" + self.routing
        expected = {
            "found-this-design": "found-this-design",
            "impeccable": "impeccable",
            "diagnosing-bugs": "diagnosing-bugs",
            "full-audit-keamanan": "full-audit-keamanan",
            "full-performance-audit": "full-performance-audit",
            "context7": "context7",
            "shadcn": "shadcn",
            "architect": "architect",
            "codebase-memory": "codebase-memory",
            "smartdoc": "smartdoc",
            "smartbook-ingest": "smartbook-ingest",
        }
        for label, needle in expected.items():
            self.assertIn(needle, blob, label)

    def test_no_context_guard_rule(self):
        self.assertFalse((ROOT / "rules" / "04-context-guard.md").exists())


if __name__ == "__main__":
    unittest.main()

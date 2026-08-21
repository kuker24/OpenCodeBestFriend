#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT))
from lib.doctor import owned_agents_block, parse_mcp_list  # noqa: E402


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


class AgentsBlockTests(unittest.TestCase):
    def test_owned_block_ignores_foreign_text(self):
        text = ("USER\n" * 200) + "<!-- OPENCODEBESTFRIEND:BEGIN -->\nrouter\n<!-- OPENCODEBESTFRIEND:END -->\n"
        block = owned_agents_block(text)
        self.assertIsNotNone(block)
        self.assertLessEqual(block.count("\n"), 5)
        self.assertGreater(text.count("\n"), 120)


if __name__ == "__main__":
    unittest.main()

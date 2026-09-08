#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TASTE_GUARD = ROOT / "skills" / "impeccable" / "reference" / "taste-guard.md"
TASTE_DIR = ROOT / "skills" / "impeccable" / "reference" / "taste"


class TasteIntegrationTests(unittest.TestCase):
    def test_canonical_taste_guard_exists(self):
        self.assertTrue(TASTE_GUARD.is_file())
        text = TASTE_GUARD.read_text(encoding="utf-8")
        self.assertIn("# Taste Quality Guard", text)
        self.assertIn("Leonxlnx/taste-skill", text)
        self.assertIn("Intent & Surface Mode", text)
        self.assertIn("Factual Content", text)
        self.assertIn("prefers-reduced-motion", text)
        self.assertIn("Observed Render", text)

    def test_taste_guard_referenced_in_impeccable(self):
        impeccable_skill = (ROOT / "skills" / "impeccable" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("reference/taste-guard.md", impeccable_skill)
        self.assertIn("reference/taste/", impeccable_skill)

    def test_contextual_taste_modules_exist(self):
        expected = ["direction.md", "composition.md", "redesign.md", "preflight.md"]
        for name in expected:
            path = TASTE_DIR / name
            self.assertTrue(path.is_file(), name)
            content = path.read_text(encoding="utf-8")
            self.assertIn("taste-skill", content)

    def test_precedence_and_anti_dogma_rules(self):
        text = TASTE_GUARD.read_text(encoding="utf-8")
        self.assertIn("Explicit brief, pinned aesthetic, brand guidelines, and user constraints always win", text)
        self.assertIn("Anti-Dogma Rule", text)
        self.assertIn("Purple accents, Inter font, SVG icons", text)

    def test_provenance_and_sources_inventory(self):
        sources = json.loads((ROOT / "vendor" / "sources.json").read_text(encoding="utf-8"))
        self.assertIn("taste-skill", sources["sources"])
        self.assertEqual(
            sources["sources"]["taste-skill"]["commit"],
            "ccbc15639c97057cbfcf32ecebc38ef716e4bb37",
        )
        lic = ROOT / "vendor" / "licenses" / "LEONXLNX-TASTE-MIT.txt"
        self.assertTrue(lic.is_file())
        self.assertIn("Copyright (c) 2026 Leonxlnx", lic.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

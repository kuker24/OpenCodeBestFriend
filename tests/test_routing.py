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
        self.assertNotIn("Scroll/3D → `scroll-world`", self.agents)
        self.assertIn("scroll-craft", self.agents)

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
            "scroll-craft": "scroll-craft",
            "humanizer": "humanizer",
            "academic": "academic",
            "hyperframes": "hyperframes",
            "diagram-design": "diagram-design",
        }
        for label, needle in expected.items():
            self.assertIn(needle, blob, label)

    def test_new_specialist_boundaries(self):
        # Academic vs research vs smartdoc
        self.assertIn("Academic literature / manuscript / peer-critique → skill `academic`", self.agents)
        self.assertIn("Scholarly literature surveys, academic manuscripts", self.routing)
        self.assertIn("academic", self.routing)
        
        # Hyperframes vs visual-studio vs scroll
        self.assertIn("Deterministic HTML video / render HTML to MP4 → skill `hyperframes`", self.agents)
        self.assertIn("Deterministic HTML composition rendered to video: `/hyperframes`", self.routing)
        self.assertIn("Ordinary scrollable UI stays `/impeccable`.", self.routing)
        
        # Diagram design vs impeccable vs codebase-design
        self.assertIn("Editorial diagram HTML/SVG → skill `diagram-design`", self.agents)
        self.assertIn("Editorial HTML and inline SVG diagrams", self.routing)
        
        # Humanizer & unslop alias
        self.assertIn("Prose AI-tells / humanize → skill `humanizer`. Slash `/unslop` is the same specialist, manual only.", self.agents)
        self.assertIn("Prose AI-tell removal and natural tone polishing: `/humanizer`.", self.routing)
        unslop_skill = (ROOT / "manual-skills" / "unslop" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("skills/humanizer/SKILL.md", unslop_skill)
        self.assertNotIn("Puffery", unslop_skill)
        self.assertNotIn("Superficial -ing phrases", unslop_skill)
        
        # Foreign harness note
        self.assertIn("ECC / other harness overlays: `FOREIGN_ON_DEMAND`", self.routing)

    def test_scroll_routes_have_explicit_boundaries(self):
        self.assertIn(
            "Scroll-led storytelling (scroll is the timeline, scrollytelling, signature interaction): `/scroll-craft`.",
            self.routing,
        )
        self.assertIn("Ordinary scrollable UI stays `/impeccable`.", self.routing)
        self.assertIn(
            "Continuous camera fly-through, diorama, or 3D-world landing: `/scroll-world` even if the request says scroll.",
            self.routing,
        )
        self.assertIn(
            "`/scroll-craft` plus Continuous World: Scroll Craft writes the brief, then `/scroll-world`.",
            self.routing,
        )
        skill = (ROOT / "skills" / "scroll-craft" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Words like `premium`, `cinematic`,", skill)
        self.assertIn("alone are not enough", skill)
        self.assertIn("Do not implement worldflight here.", skill)

    def test_no_context_guard_rule(self):
        self.assertFalse((ROOT / "rules" / "04-context-guard.md").exists())


if __name__ == "__main__":
    unittest.main()

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
            "agent-architecture-audit": "agent-architecture-audit",
            "eval-harness": "eval-harness",
            "cost-aware-llm-pipeline": "cost-aware-llm-pipeline",
            "prompt-optimizer": "prompt-optimizer",
            "skill-stocktake": "skill-stocktake",
            "api-design": "api-design",
            "contract-first": "contract-first",
            "automation-audit-ops": "automation-audit-ops",
            "code-tour": "code-tour",
            "click-path-audit": "click-path-audit",
            "supabase-ops": "supabase-ops",
            "mongodb-ops": "mongodb-ops",
            "vercel-ops": "vercel-ops",
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

        # Warehouse Wave 2 specialists
        self.assertIn("agent-architecture-audit", self.agents)
        self.assertIn("eval-harness", self.agents)
        self.assertIn("cost-aware-llm-pipeline", self.agents)
        self.assertIn("prompt-optimizer", self.agents)
        self.assertIn("skill-stocktake", self.agents)
        self.assertIn("Agent stack diagnostics / context leak / wrapper regression → skill `agent-architecture-audit`", self.agents)
        self.assertIn("Benchmark agent / pass@k → skill `eval-harness`", self.agents)
        self.assertIn("Token budget / model tier / prompt cache → skill `cost-aware-llm-pipeline`", self.agents)
        self.assertIn("Structural prompt critique → skill `prompt-optimizer`", self.agents)
        self.assertIn("Skill catalog hygiene → skill `skill-stocktake`", self.agents)
        self.assertIn("Agent architecture diagnosis, autonomous loop failures", self.routing)
        self.assertIn("Evaluation harness, prompt/agent benchmarks", self.routing)
        self.assertIn("Cost-aware LLM architectures, complexity model tiering", self.routing)
        self.assertIn("Prompt critique, structural optimization", self.routing)
        self.assertIn("OpenCodeBestFriend skill catalog hygiene", self.routing)

        # Warehouse Wave 3 specialists
        self.assertIn("api-design", self.agents)
        self.assertIn("contract-first", self.agents)
        self.assertIn("automation-audit-ops", self.agents)
        self.assertIn("code-tour", self.agents)
        self.assertIn("click-path-audit", self.agents)
        self.assertIn("REST resource/status/pagination/versioning → skill `api-design`", self.agents)
        self.assertIn("Consumer/provider OpenAPI/AsyncAPI/Protobuf → skill `contract-first`", self.agents)
        self.assertIn("Live cron/CI/hook/MCP inventory keep-merge-cut → skill `automation-audit-ops`", self.agents)
        self.assertIn("CodeTour .tour + anchor file → skill `code-tour`", self.agents)
        self.assertIn("Handler vs shared-store sequential-undo → skill `click-path-audit`", self.agents)
        self.assertIn("REST resource, status, pagination, and versioning design: `/api-design`", self.routing)
        self.assertIn("Consumer/provider OpenAPI, AsyncAPI, or Protobuf contracts: `/contract-first`", self.routing)
        self.assertIn("Live cron, CI, hook, MCP, and wrapper inventory", self.routing)
        self.assertIn("CodeTour `.tour` walkthroughs with verified file anchors: `/code-tour`", self.routing)
        self.assertIn("Button/handler sequential-undo and shared-store side effects: `/click-path-audit`", self.routing)

        # Ensure all required named specialists appear in both AGENTS.md and 00-routing.md
        required_specialists = [
            "api-design",
            "contract-first",
            "automation-audit-ops",
            "code-tour",
            "click-path-audit",
            "agent-architecture-audit",
            "eval-harness",
            "cost-aware-llm-pipeline",
            "prompt-optimizer",
            "skill-stocktake",
            "found-this-design",
            "impeccable",
            "hyperframes",
            "scroll-craft",
            "scroll-world",
            "diagram-design",
            "smartdoc",
            "academic",
            "humanizer",
            "supabase-ops",
            "mongodb-ops",
            "vercel-ops",
        ]
        for spec in required_specialists:
            self.assertIn(spec, self.agents, f"Expected {spec} in AGENTS.md")
            self.assertIn(spec, self.routing, f"Expected {spec} in 00-routing.md")

    def test_vendor_ops_boundaries(self):
        self.assertIn("Supabase Auth/RLS/migrations/Edge → skill `supabase-ops`", self.agents)
        self.assertIn("Mongo schema/index/aggregation → skill `mongodb-ops`", self.agents)
        self.assertIn("Vercel/Next hosting/deploy config → skill `vercel-ops`", self.agents)
        self.assertIn("Supabase Auth, RLS policies, migrations, Edge Functions: `/supabase-ops`", self.routing)
        self.assertIn("MongoDB schemas, indexing, aggregation pipelines: `/mongodb-ops`", self.routing)
        self.assertIn("Vercel deployment, `vercel.json`, preview URLs, hosting config: `/vercel-ops`", self.routing)
        self.assertIn("FOREIGN vendor packs", self.routing)
        self.assertIn("Do not use vendor `frontend-design` for product UI", self.routing)

    def test_ui_atoms_clause(self):
        needle = "UI atoms → impeccable after Design V2 shortlist; BANK_MISS ≠ generate"
        self.assertIn(needle, self.routing)
        self.assertIn("UI atoms (button, input, card, nav) after world/brief → impeccable after Design V2 shortlist; BANK_MISS ≠ generate", self.agents)

    def test_stitch_routing_boundary(self):
        needle = "Stitch MCP = screen/comp generation only; then found-this-design or impeccable + Design V2 atoms. Never implement production UI from Stitch alone."
        self.assertIn(needle, self.agents)
        self.assertIn("Never implement production UI from Stitch alone", self.routing)
        self.assertIn("never implement production UI from Stitch alone", (ROOT / "docs" / "routing.md").read_text(encoding="utf-8"))
        self.assertIn("Do not use Stitch as an automatic UI implementer", self.routing)
        impeccable = (ROOT / "skills" / "impeccable" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Stitch screen", impeccable)
        self.assertIn("approved comp", impeccable)

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

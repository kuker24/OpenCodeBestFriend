#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT))
from lib.common import load_policy  # noqa: E402

SKILL = ROOT / "skills" / "scroll-craft"
FM = re.compile(r"\A---\n(.*?\n)---\n", re.DOTALL)
REFS = (
    "journey.md",
    "grammars.md",
    "devices.md",
    "signature-fingerprint.md",
    "hero-depth.md",
    "mobile-accessibility.md",
    "verification.md",
    "handoff.md",
)
ROUTING_CASES = (
    ("Create normal dashboard", "impeccable"),
    ("storytelling website controlled by scroll", "scroll-craft"),
    ("continuous camera fly-through", "scroll-world"),
    ("Polish button easing", "emil-design-eng"),
    ("Create product photo", "visual-studio"),
)


class ScrollCraftContractTests(unittest.TestCase):
    def test_policy_model_invoked(self):
        allow, skills, model, manual = load_policy(ROOT)
        self.assertIn("scroll-craft", allow)
        self.assertEqual(skills["scroll-craft"]["invocation"], "model")
        self.assertIn("scroll-craft", model)
        self.assertNotIn("scroll-craft", manual)
        self.assertFalse((ROOT / "commands" / "scroll-craft.md").exists())
        self.assertFalse((ROOT / "manual-skills" / "scroll-craft").exists())

    def test_frontmatter_and_references(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        fm = FM.match(text)
        self.assertIsNotNone(fm)
        assert fm is not None
        block = fm.group(1)
        self.assertIn("name: scroll-craft", block)
        self.assertIn("compatibility: opencode", block)
        self.assertIn("license: MIT", block)
        self.assertNotIn("allowed-tools", block)
        self.assertNotIn("disable-model-invocation", block)
        self.assertLessEqual(text.count("\n"), 200)
        for name in REFS:
            path = SKILL / "references" / name
            self.assertTrue(path.is_file(), name)
            self.assertIn(f"references/{name}", text)
        notice = (SKILL / "NOTICE.md").read_text(encoding="utf-8")
        self.assertIn("Copyright (c) 2026 Nate Herk", notice)
        self.assertIn("MIT License", notice)

    def test_engine_contract(self):
        js = (SKILL / "engine" / "scrollcraft.js").read_text(encoding="utf-8")
        css = (SKILL / "engine" / "scrollcraft.css").read_text(encoding="utf-8")
        theme = (SKILL / "engine" / "scrollcraft-theme.css").read_text(encoding="utf-8")
        self.assertTrue(css)
        self.assertTrue(theme)
        self.assertIn("function mount(", js)
        self.assertIn("function destroy()", js)
        self.assertIn("--sc-p", js)
        self.assertIn("prefers-reduced-motion", js)
        self.assertIn("reduceMQ.addEventListener", js)
        self.assertIn("requestAnimationFrame", js)
        fetch_at = js.find("fetch(")
        self.assertGreater(fetch_at, 0)
        self.assertGreater(fetch_at, js.find("function loadClip"))
        self.assertIn("new AbortController()", js)
        self.assertIn("URL.revokeObjectURL", js)
        self.assertIn("cancelAnimationFrame", js)
        self.assertIn("clearTimeout", js)
        self.assertIn("observers.forEach", js)
        self.assertIn("readyRoot.classList.remove('sc-ready')", js)
        self.assertIn("[data-sc-cue] { opacity: 1", css)
        self.assertNotIn("worldflight", (js + css).lower())
        self.assertNotIn("worlds:", js)
        self.assertIn('.sc-theme :focus-visible', theme)
        for selector in ("html", "body", "*", "a", "button", "input", "select", "textarea", "table"):
            self.assertIsNone(
                re.search(rf"(?m)^\s*{re.escape(selector)}(?:\b|\s*[,{{:*])", css),
                f"global {selector} selector in mechanism CSS",
            )
        self.assertNotIn("KIE_AI_API_KEY", js)
        self.assertNotIn("playwright-core", js)
        self.assertNotIn("higgsfield", js.lower())

    def test_no_runtime_provider_coupling(self):
        runtime = ""
        for rel in (
            "SKILL.md",
            "engine/scrollcraft.js",
            "engine/scrollcraft.css",
            "engine/scrollcraft-theme.css",
        ):
            runtime += (SKILL / rel).read_text(encoding="utf-8") + "\n"
        self.assertNotIn("KIE_AI_API_KEY", runtime)
        self.assertNotIn("playwright-core", runtime)
        self.assertNotIn("npm i playwright", runtime)
        handoff = (SKILL / "references" / "handoff.md").read_text(encoding="utf-8")
        self.assertIn("scroll-world", handoff)
        self.assertIn("Continuous World", handoff)
        self.assertIn("browser-act", handoff)
        ver = (SKILL / "references" / "verification.md").read_text(encoding="utf-8")
        self.assertIn("chrome-direct", ver)
        self.assertIn("act progress", ver.lower())
        fp = (SKILL / "references" / "signature-fingerprint.md").read_text(encoding="utf-8")
        self.assertIn("NO_HISTORY", fp)
        self.assertIn(".scratch/scroll-craft/", fp)

    def test_routing_docs(self):
        agents = (ROOT / "templates" / "AGENTS.md").read_text(encoding="utf-8")
        routing = (ROOT / "rules" / "00-routing.md").read_text(encoding="utf-8")
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        blob = agents + "\n" + routing + "\n" + skill
        self.assertNotIn("Scroll/3D → `scroll-world`", agents)
        self.assertIn("scroll-craft", agents)
        self.assertIn("scroll-world", agents)
        self.assertIn("scroll-craft", routing)
        for request, owner in ROUTING_CASES:
            self.assertIn(owner, blob, request)
        self.assertIn("impeccable", skill.lower())
        self.assertIn("/scroll-craft", skill)

    def test_fixture_offline_semantic(self):
        fx = ROOT / "tests" / "fixtures" / "scroll-craft"
        html = (fx / "index.html").read_text(encoding="utf-8")
        css = (fx / "page.css").read_text(encoding="utf-8")
        self.assertIn("<h1", html)
        self.assertIn('href="#cta"', html)
        self.assertIn("Synthetic demonstration", html)
        self.assertIn("data-sc-parallax", html)
        self.assertIn("data-sc-pan", html)
        self.assertIn("prefers-reduced-motion", css)
        self.assertIn("grid", css)
        self.assertTrue((fx / "assets" / "bg.svg").is_file())
        self.assertTrue((fx / "assets" / "mid.svg").is_file())
        self.assertTrue((fx / "assets" / "fg.svg").is_file())
        self.assertNotIn("https://", html)
        self.assertNotIn("http://", html)
        self.assertNotIn("https://", css)
        self.assertIn("scrollcraft.js", html)
        self.assertIn("scrollcraft-theme.css", html)
        self.assertIn('class="sc-theme"', html)
        self.assertIn("ScrollCraft.mount", html)
        self.assertNotIn("<video", html)

    def test_real_browser_gate_is_wired(self):
        smoke = ROOT / "tests" / "scroll_craft_browser_smoke.mjs"
        self.assertTrue(smoke.is_file())
        text = smoke.read_text(encoding="utf-8")
        self.assertIn("Emulation.setDeviceMetricsOverride", text)
        self.assertIn("prefers-reduced-motion", text)
        self.assertIn("Input.dispatchKeyEvent", text)
        self.assertIn("fetchSignals", text)
        self.assertIn("revokedUrls", text)
        self.assertNotIn("playwright", text.lower())
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertIn("browser-smoke:", workflow)
        self.assertIn("node tests/scroll_craft_browser_smoke.mjs", workflow)
        self.assertIn('chrome-version: "1692935"', workflow)

    def test_license_inventory(self):
        audit = json.loads((ROOT / "vendor" / "license-audit.json").read_text(encoding="utf-8"))
        self.assertEqual(audit["skills"]["scroll-craft"]["license"], "MIT")
        self.assertEqual(audit["skills"]["scroll-craft"]["redistribution"], "mit")
        lic = ROOT / "vendor" / "licenses" / "NATEHERK-SCROLL-CRAFT-MIT.txt"
        self.assertTrue(lic.is_file())
        text = lic.read_text(encoding="utf-8")
        self.assertIn("Copyright (c) 2026 Nate Herk", text)
        self.assertIn("Permission is hereby granted", text)
        sources = json.loads((ROOT / "vendor" / "sources.json").read_text(encoding="utf-8"))
        self.assertEqual(
            sources["sources"]["scroll-craft"]["commit"],
            "0b816225945e45380397d6a0487efa3c98916858",
        )


if __name__ == "__main__":
    unittest.main()

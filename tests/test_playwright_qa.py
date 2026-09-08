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
from lib.doctor import Findings, _browser_qa_findings  # noqa: E402

SKILL = ROOT / "skills" / "playwright-qa"
FM = re.compile(r"\A---\n(.*?\n)---\n", re.DOTALL)
REFS = ("workflow.md", "sessions.md", "setup.md")


class PlaywrightQAContractTests(unittest.TestCase):
    def test_policy_model_invoked(self):
        allow, skills, model, manual = load_policy(ROOT)
        self.assertIn("playwright-qa", allow)
        self.assertEqual(skills["playwright-qa"]["invocation"], "model")
        self.assertIn("playwright-qa", model)
        self.assertNotIn("playwright-qa", manual)
        self.assertFalse((ROOT / "commands" / "playwright-qa.md").exists())
        self.assertFalse((ROOT / "manual-skills" / "playwright-qa").exists())

    def test_frontmatter_and_references(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        fm = FM.match(text)
        self.assertIsNotNone(fm)
        assert fm is not None
        block = fm.group(1)
        self.assertIn("name: playwright-qa", block)
        self.assertIn("compatibility: opencode", block)
        self.assertIn("license: Apache-2.0", block)
        self.assertNotIn("allowed-tools", block)
        self.assertNotIn("disable-model-invocation", block)
        self.assertLessEqual(text.count("\n"), 200)
        for name in REFS:
            path = SKILL / "references" / name
            self.assertTrue(path.is_file(), name)
            self.assertIn(f"references/{name}", text)
        notice = (SKILL / "NOTICE.md").read_text(encoding="utf-8")
        self.assertIn("Copyright (c) Microsoft Corporation", notice)
        self.assertIn("655530f6d0dc71a0d6bf46ae165877d3c7311099", notice)
        self.assertIn("Apache License 2.0", notice)

    def test_session_isolation_and_discipline(self):
        sessions = (SKILL / "references" / "sessions.md").read_text(encoding="utf-8")
        self.assertIn("-s=", sessions)
        self.assertIn("close-all", sessions)
        self.assertIn("kill-all", sessions)
        self.assertIn("strictly forbidden", sessions.lower())
        workflow = (SKILL / "references" / "workflow.md").read_text(encoding="utf-8")
        self.assertIn("snapshot", workflow)
        self.assertIn("No fixed sleep", workflow)

    def test_doctor_browser_findings_safe(self):
        f = Findings()
        _browser_qa_findings(f)
        labels = [item[1] for item in f.items]
        self.assertIn("Playwright CLI", labels)
        self.assertIn("Playwright browsers", labels)
        self.assertIn("Project E2E suite", labels)
        self.assertIn("Browser launch probe", labels)
        self.assertIn("BrowserAct CLI", labels)

    def test_license_inventory(self):
        audit = json.loads((ROOT / "vendor" / "license-audit.json").read_text(encoding="utf-8"))
        self.assertEqual(audit["skills"]["playwright-qa"]["license"], "Apache-2.0")
        self.assertEqual(audit["skills"]["playwright-qa"]["redistribution"], "apache-2.0")
        lic = ROOT / "vendor" / "licenses" / "MICROSOFT-PLAYWRIGHT-CLI-APACHE2.txt"
        self.assertTrue(lic.is_file())
        text = lic.read_text(encoding="utf-8")
        self.assertIn("Apache License", text)
        self.assertIn("Copyright (c) Microsoft Corporation.", text)
        sources = json.loads((ROOT / "vendor" / "sources.json").read_text(encoding="utf-8"))
        self.assertEqual(
            sources["sources"]["playwright-cli"]["commit"],
            "655530f6d0dc71a0d6bf46ae165877d3c7311099",
        )


if __name__ == "__main__":
    unittest.main()

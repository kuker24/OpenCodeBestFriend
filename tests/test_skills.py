#!/usr/bin/env python3
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT))
from lib.common import load_policy  # noqa: E402

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FM = re.compile(r"\A---\n(.*?\n)---\n", re.DOTALL)


class SkillPolicyTests(unittest.TestCase):
    def test_counts(self):
        allow, skills, model, manual = load_policy(ROOT)
        self.assertEqual(len(allow), 40)
        self.assertEqual(len(model), 24)
        self.assertEqual(len(manual), 16)
        self.assertEqual(set(allow), set(skills))

    def test_model_skills_exist(self):
        _, _, model, manual = load_policy(ROOT)
        for name in model:
            skill = ROOT / "skills" / name / "SKILL.md"
            self.assertTrue(skill.is_file(), name)
            self.assertTrue(NAME_RE.match(name), name)
            text = skill.read_text(encoding="utf-8")
            fm = FM.match(text)
            self.assertIsNotNone(fm, name)
            self.assertNotIn("disable-model-invocation", fm.group(1))
            self.assertNotIn("user-invocable", fm.group(1))
            self.assertTrue((ROOT / "manual-skills" / name).exists() is False)

    def test_manual_not_in_discovery(self):
        _, _, _, manual = load_policy(ROOT)
        for name in manual:
            self.assertTrue((ROOT / "manual-skills" / name / "SKILL.md").is_file(), name)
            self.assertTrue((ROOT / "commands" / f"{name}.md").is_file(), name)
            self.assertFalse((ROOT / "skills" / name).exists(), name)

    def test_rules(self):
        names = {p.name for p in (ROOT / "rules").glob("*.md")}
        self.assertEqual(len(names), 6)
        self.assertNotIn("04-context-guard.md", names)


if __name__ == "__main__":
    unittest.main()

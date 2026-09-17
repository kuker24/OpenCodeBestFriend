#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT))
from lib.common import load_policy  # noqa: E402

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FM = re.compile(r"\A---\n(.*?\n)---\n", re.DOTALL)
KEY_RE = re.compile(r"^([a-z][a-z0-9_-]*):\s*(.*)$")
TOKEN_RE = re.compile(r"[a-z0-9]+")
FOREIGN_PATH_RE = re.compile(r"~/\.claude\b")

OVERLAP_WARN = 0.50
OVERLAP_FAIL = 0.75


def frontmatter(path: Path) -> dict[str, str]:
    fm = FM.match(path.read_text(encoding="utf-8"))
    if fm is None:
        return {}
    out: dict[str, str] = {}
    for line in fm.group(1).splitlines():
        m = KEY_RE.match(line)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


def skill_files() -> list[tuple[str, Path]]:
    found = []
    for base in ("skills", "manual-skills"):
        for path in sorted((ROOT / base).glob("*/SKILL.md")):
            found.append((path.parent.name, path))
    return found


def normalize_license(value: str) -> str:
    text = value.strip().strip('"').strip("'").strip()
    return text.replace("Apache 2.0", "Apache-2.0")


def jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 0.0


class SkillPolicyTests(unittest.TestCase):
    def test_counts(self):
        allow, skills, model, manual = load_policy(ROOT)
        self.assertEqual(len(allow), 62)
        self.assertEqual(len(model), 47)
        self.assertEqual(len(manual), 15)
        self.assertEqual(set(allow), set(skills))
        for name in ("supabase-ops", "mongodb-ops", "vercel-ops", "img2threejs", "markitdown", "id-demo-video"):
            self.assertIn(name, allow)
            self.assertIn(name, model)
        self.assertIn("demo-video", manual)

    def test_model_skills_exist(self):
        _, _, model, manual = load_policy(ROOT)
        for name in model:
            skill = ROOT / "skills" / name / "SKILL.md"
            self.assertTrue(skill.is_file(), name)
            self.assertTrue(NAME_RE.match(name), name)
            text = skill.read_text(encoding="utf-8")
            fm = FM.match(text)
            self.assertIsNotNone(fm, name)
            assert fm is not None
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

    def test_policy_matches_measured_tree(self):
        allow, _, model, manual = load_policy(ROOT)
        on_disk_model = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}
        on_disk_manual = {p.parent.name for p in (ROOT / "manual-skills").glob("*/SKILL.md")}
        on_disk_commands = {p.stem for p in (ROOT / "commands").glob("*.md")}
        self.assertEqual(on_disk_model, set(model))
        self.assertEqual(on_disk_manual, set(manual))
        self.assertEqual(on_disk_commands, set(manual))
        self.assertEqual(len(allow), len(on_disk_model) + len(on_disk_manual))

    def test_no_model_manual_name_collision(self):
        _, _, model, manual = load_policy(ROOT)
        self.assertEqual(set(model) & set(manual), set())
        commands = {p.stem for p in (ROOT / "commands").glob("*.md")}
        self.assertEqual(set(model) & commands, set())


class SkillFrontmatterTests(unittest.TestCase):
    def test_required_keys(self):
        for name, path in skill_files():
            with self.subTest(skill=name):
                fm = frontmatter(path)
                self.assertTrue(fm, name)
                self.assertEqual(fm.get("name"), name)
                self.assertEqual(fm.get("compatibility"), "opencode")
                self.assertTrue((fm.get("description") or "").strip())

    def test_license_evidence(self):
        # A missing frontmatter license is not a grant: vendor/license-audit.json
        # is the evidence source. Frontmatter, when present, must not contradict it.
        audit = json.loads(
            (ROOT / "vendor" / "license-audit.json").read_text(encoding="utf-8")
        )["skills"]
        for name, path in skill_files():
            with self.subTest(skill=name):
                self.assertIn(name, audit, name)
                approved = audit[name]["license"]
                self.assertIn(approved, {"MIT", "Apache-2.0"}, name)
                self.assertTrue(str(audit[name].get("evidence", "")).strip(), name)
                declared = frontmatter(path).get("license")
                if declared:
                    self.assertEqual(normalize_license(declared), approved, name)

    def test_description_overlap(self):
        rows = []
        for name, path in skill_files():
            desc = frontmatter(path).get("description", "")
            rows.append((name, set(TOKEN_RE.findall(desc.lower()))))
        failures = []
        for (left, a), (right, b) in itertools.combinations(rows, 2):
            score = jaccard(a, b)
            if score >= OVERLAP_FAIL:
                failures.append(f"{left} ~ {right} = {score:.2f}")
        self.assertEqual(failures, [], f"description overlap >= {OVERLAP_FAIL}: {failures}")

    def test_no_foreign_runtime_path(self):
        for name, path in skill_files():
            with self.subTest(skill=name):
                text = path.read_text(encoding="utf-8")
                self.assertIsNone(FOREIGN_PATH_RE.search(text), name)


if __name__ == "__main__":
    unittest.main()

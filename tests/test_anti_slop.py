#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT))
from lib.common import load_policy  # noqa: E402

SKILL = ROOT / "skills" / "install-anti-slop"
FM = re.compile(r"\A---\n(.*?\n)---\n", re.DOTALL)
EXPECTED_RULES = (
    "no-chained-type-assertions.ts",
    "no-conditional-empty-object-spread.ts",
    "no-known-value-widening.ts",
    "no-module-mocking.ts",
    "no-object-parameters.ts",
    "no-reflect-apply.ts",
    "no-reflect-get.ts",
    "no-runtime-typeof.ts",
    "no-shape-in-symbol-names.ts",
    "no-unknown-parameters.ts",
    "no-unknown-returns.ts",
    "no-unknown-type-aliases.ts",
    "no-unsafe-dictionary-type.ts",
    "no-widen-then-assert.ts",
    "require-safety-comment-for-type-assertion.ts",
)


class AntiSlopContractTests(unittest.TestCase):
    def test_policy_model_invoked(self):
        allow, skills, model, manual = load_policy(ROOT)
        self.assertIn("install-anti-slop", allow)
        self.assertEqual(skills["install-anti-slop"]["invocation"], "model")
        self.assertIn("install-anti-slop", model)
        self.assertNotIn("install-anti-slop", manual)
        self.assertFalse((ROOT / "commands" / "install-anti-slop.md").exists())
        self.assertFalse((ROOT / "manual-skills" / "install-anti-slop").exists())

    def test_frontmatter_and_separation_from_unslop(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        fm = FM.match(text)
        self.assertIsNotNone(fm)
        assert fm is not None
        block = fm.group(1)
        self.assertIn("name: install-anti-slop", block)
        self.assertIn("compatibility: opencode", block)
        self.assertIn("license: MIT", block)
        self.assertIn("prose editing (use /unslop)", block)
        self.assertLessEqual(text.count("\n"), 200)

    def test_vendored_rule_snapshot_exists(self):
        assets = SKILL / "assets" / "anti-slop"
        self.assertTrue((assets / "index.ts").is_file())
        self.assertTrue((assets / "effect" / "index.ts").is_file())
        self.assertTrue((assets / "effect" / "rules" / "no-service-constructor-imports.ts").is_file())
        for rule_file in EXPECTED_RULES:
            path = assets / "rules" / rule_file
            self.assertTrue(path.is_file(), rule_file)
        shared = assets / "shared"
        for shared_file in (
            "dictionary-types.ts",
            "function-parameters.ts",
            "type-alias-resolution.ts",
            "lexical-type-parameters.ts",
            "reflect-method.ts",
        ):
            self.assertTrue((shared / shared_file).is_file(), shared_file)

    def test_license_and_sources_inventory(self):
        audit = json.loads((ROOT / "vendor" / "license-audit.json").read_text(encoding="utf-8"))
        self.assertEqual(audit["skills"]["install-anti-slop"]["license"], "MIT")
        self.assertEqual(audit["skills"]["install-anti-slop"]["redistribution"], "mit")
        lic = ROOT / "vendor" / "licenses" / "DMMULROY-ANTI-SLOP-MIT.txt"
        self.assertTrue(lic.is_file())
        text = lic.read_text(encoding="utf-8")
        self.assertIn("Copyright (c) 2026 Dillon Mulroy", text)
        sources = json.loads((ROOT / "vendor" / "sources.json").read_text(encoding="utf-8"))
        self.assertEqual(
            sources["sources"]["anti-slop"]["commit"],
            "e8c4880471b23ab7f216fba7b27d173a6ef07d4c",
        )
        self.assertEqual(sources["sources"]["anti-slop"]["version"], "0.1.2")

    def test_manage_script_audit_mode_zero_mutations(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            manage_script = SKILL / "scripts" / "manage.mjs"
            res = subprocess.run(
                ["node", str(manage_script), "audit", "--json"],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                check=True,
            )
            data = json.loads(res.stdout)
            self.assertEqual(data["mode"], "audit")
            self.assertEqual(data["mutations"], 0)
            self.assertTrue(data["clean"])
            self.assertEqual(list(Path(tmpdir).iterdir()), [])

    def test_manage_script_install_recommended_and_remove(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            manage_script = SKILL / "scripts" / "manage.mjs"
            # 1. Install recommended
            res = subprocess.run(
                ["node", str(manage_script), "install", "--profile", "recommended"],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertIn("Installed anti-slop plugin (recommended)", res.stdout)
            copied_entry = Path(tmpdir) / "tools" / "oxlint" / "anti-slop" / "index.ts"
            self.assertTrue(copied_entry.is_file())
            config_ts = Path(tmpdir) / "oxlint.config.ts"
            self.assertTrue(config_ts.is_file())
            content = config_ts.read_text(encoding="utf-8")
            self.assertIn("anti-slop/no-chained-type-assertions", content)
            self.assertIn("anti-slop/no-widen-then-assert", content)

            # 2. Re-install without force refuses overwrite
            res_refuse = subprocess.run(
                ["node", str(manage_script), "install", "--profile", "recommended"],
                cwd=tmpdir,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(res_refuse.returncode, 0)
            self.assertIn("Refusing to overwrite", res_refuse.stderr)

            # 3. Remove
            res_remove = subprocess.run(
                ["node", str(manage_script), "remove"],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertIn("Removed anti-slop", res_remove.stdout)
            self.assertFalse(copied_entry.exists())
            self.assertFalse(config_ts.exists())

    def test_manage_script_strict_and_effect_options(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            manage_script = SKILL / "scripts" / "manage.mjs"
            res = subprocess.run(
                ["node", str(manage_script), "install", "--profile", "strict", "--with-effect"],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertIn("Installed anti-slop plugin (strict)", res.stdout)
            config_ts = Path(tmpdir) / "oxlint.config.ts"
            content = config_ts.read_text(encoding="utf-8")
            self.assertIn("anti-slop/no-module-mocking", content)
            self.assertIn("anti-slop-effect/no-service-constructor-imports", content)


if __name__ == "__main__":
    unittest.main()

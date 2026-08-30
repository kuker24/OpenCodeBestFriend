#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import json
import os
import sys
import unittest
import zipfile
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.cli import main as cli_main  # noqa: E402
from lib.design_v2.bank import (  # noqa: E402
    PathEscape,
    assert_under_v2,
    bank_present,
    list_sources,
    resolve_design_v2_root,
)
from lib.design_v2.dna import extract_query  # noqa: E402
from lib.design_v2.import_stage import ImportRejected, import_stage  # noqa: E402
from lib.design_v2.rebuild import rebuild  # noqa: E402
from lib.design_v2.schema import check_item, empty_item_v1, empty_item_v2  # noqa: E402
from lib.design_v2.search import search, shortlist  # noqa: E402
from lib.install import cmd_uninstall  # noqa: E402
from lib.paths import assert_within_allowed  # noqa: E402
from tests.support import IsolatedHome  # noqa: E402


def _item(**overrides):
    row = empty_item_v2()
    row.update(overrides)
    if "id" in overrides and "canonical_id" not in overrides:
        row["canonical_id"] = overrides["id"]
    return row


class DesignV2Tests(IsolatedHome):
    def setUp(self):
        super().setUp()
        self.bank = self.tmp / "DesignV2"
        os.environ["OPENCODE_DESIGN_V2"] = str(self.bank)
        os.environ.pop("OPENCODE_DESIGN_V2_SKIP_FTS", None)
        os.environ.pop("GROK_DESIGN_V2", None)
        os.environ.pop("GROK_DESIGN_V2_SKIP_FTS", None)

    def tearDown(self):
        os.environ.pop("OPENCODE_DESIGN_V2", None)
        os.environ.pop("OPENCODE_DESIGN_V2_SKIP_FTS", None)
        os.environ.pop("GROK_DESIGN_V2", None)
        os.environ.pop("GROK_DESIGN_V2_SKIP_FTS", None)
        super().tearDown()

    def _inbox(self, item: dict) -> None:
        inbox = self.bank / "inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        (inbox / f"{item['id'].replace(':', '-')}.json").write_text(
            json.dumps(item, indent=2) + "\n", encoding="utf-8"
        )

    def test_root_env_vs_default(self):
        os.environ.pop("OPENCODE_DESIGN_V2", None)
        default = resolve_design_v2_root()
        self.assertEqual(default, (self.tmp / "DesignV2").resolve())
        os.environ["OPENCODE_DESIGN_V2"] = str(self.tmp / "other")
        self.assertEqual(resolve_design_v2_root(), (self.tmp / "other").resolve())

    def test_grok_design_v2_alias(self):
        os.environ.pop("OPENCODE_DESIGN_V2", None)
        os.environ["GROK_DESIGN_V2"] = str(self.tmp / "legacy")
        self.assertEqual(resolve_design_v2_root(), (self.tmp / "legacy").resolve())
        os.environ["OPENCODE_DESIGN_V2"] = str(self.tmp / "canonical")
        self.assertEqual(resolve_design_v2_root(), (self.tmp / "canonical").resolve())

    def test_path_escape_rejected(self):
        self.bank.mkdir()
        with self.assertRaises(PathEscape):
            assert_under_v2(self.bank, self.tmp / "outside.txt")
        with self.assertRaises(PathEscape):
            assert_under_v2(self.bank, self.bank / ".." / "etc")

    def test_owned_namespace_rejects_design_v2(self):
        self.bank.mkdir()
        with self.assertRaises(SystemExit):
            assert_within_allowed(self.bank)

    def test_schema_v1_and_v2(self):
        self.assertEqual(check_item(empty_item_v1()), [])
        self.assertEqual(check_item(empty_item_v2()), [])
        bad = empty_item_v2()
        bad["kind"] = "unknown-kind"
        self.assertTrue(check_item(bad))
        bad_lic = empty_item_v2()
        bad_lic["license"]["redistribution"] = "yes"
        self.assertTrue(any("redistribution" in err for err in check_item(bad_lic)))

    def test_dna_extract(self):
        extracted = extract_query("cybersecurity premium dark dense dashboard jangan slop")
        self.assertIn("luxury", extracted["aesthetic"])
        self.assertIn("dark", extracted["aesthetic"])
        self.assertEqual(extracted["density"], "dense")
        self.assertIn("security", extracted["product_fit"])
        self.assertTrue(extracted["avoid_slop"])

    def test_readonly_does_not_create_bank(self):
        self.assertFalse(self.bank.exists())
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(cli_main(["design", "status"]), 0)
            self.assertEqual(cli_main(["design", "search", "hero"]), 0)
            self.assertEqual(cli_main(["design", "inspect", "section:missing"]), 1)
            self.assertEqual(cli_main(["design", "doctor"]), 0)
            self.assertEqual(cli_main(["design", "sources"]), 0)
            self.assertEqual(cli_main(["design", "shortlist", "hero"]), 0)
        self.assertFalse(self.bank.exists())
        self.assertFalse(bank_present(self.bank))
        from lib.design_v2.commands import product_doctor_rows

        rows = product_doctor_rows()
        statuses = {label: status for status, label, _ in rows}
        self.assertEqual(statuses.get("Design V2"), "EMPTY")

    def test_rebuild_atomic_and_search(self):
        hero = _item(
            id="section:cyber-hero",
            name="Cyber security hero",
            description="Dark dense professional monitoring hero",
            kind="section",
            tags=["security", "dark", "hero"],
            categories=["hero"],
            dna={"aesthetic": ["futuristic", "dark"], "density": "dense", "geometry": "sharp"},
            product_fit=["security", "dashboard"],
            anti_slop=[],
            search_text="cybersecurity dashboard hero dark dense",
        )
        glass = _item(
            id="section:glass-hero",
            name="Glass glow hero",
            description="Generic saas gradient glow glassmorphism",
            kind="section",
            tags=["hero", "excessive-glassmorphism", "excessive-glow"],
            categories=["hero"],
            dna={"aesthetic": ["playful"], "density": "sparse"},
            anti_slop=["excessive-glassmorphism", "excessive-glow", "generic-saas-hero"],
            search_text="glass glow gradient saas hero",
        )
        self._inbox(hero)
        self._inbox(glass)
        result = rebuild(self.bank)
        self.assertEqual(result["status"], "ok")
        lock = json.loads((self.bank / "catalog" / "catalog.lock.json").read_text(encoding="utf-8"))
        self.assertEqual(lock["schema_version"], 2)
        self.assertIn("fts", lock)
        jsonl = self.bank / "catalog" / lock["jsonl_filename"]
        self.assertTrue(jsonl.is_file())
        hits = search("cybersecurity premium dark dense dashboard jangan slop")
        ids = [row["id"] for row in hits["results"]]
        self.assertIn("section:cyber-hero", ids)
        self.assertGreater(ids.index("section:cyber-hero") if "section:cyber-hero" in ids else 99, -1)
        if "section:glass-hero" in ids:
            self.assertLess(ids.index("section:cyber-hero"), ids.index("section:glass-hero"))

    def test_empty_search_and_skip_fts(self):
        os.environ["OPENCODE_DESIGN_V2_SKIP_FTS"] = "1"
        rebuild(self.bank)
        lock = json.loads((self.bank / "catalog" / "catalog.lock.json").read_text(encoding="utf-8"))
        self.assertEqual(lock["fts"]["status"], "skipped")
        self.assertTrue((self.bank / "catalog" / lock["jsonl_filename"]).is_file())
        hits = search("anything")
        self.assertEqual(hits["results"], [])
        self.assertEqual(hits["retrieval"], "jsonl")
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(cli_main(["design", "doctor"]), 0)
        self.assertIn("DEGRADED_FTS", buf.getvalue())

    def test_import_stage_rejects_symlink_and_secret(self):
        src = self.tmp / "payload"
        src.mkdir()
        (src / "ok.html").write_text("<html></html>\n", encoding="utf-8")
        evil = self.tmp / "outside.txt"
        evil.write_text("nope\n", encoding="utf-8")
        link = src / "link.html"
        link.symlink_to(evil)
        with self.assertRaises(ImportRejected):
            import_stage(src, self.bank)
        sources = self.bank / "sources" / "manual"
        if sources.is_dir():
            self.assertEqual(list(sources.iterdir()), [])

        clean = self.tmp / "clean"
        clean.mkdir()
        (clean / "page.html").write_text("<p>ok</p>\n", encoding="utf-8")
        (clean / "notes.md").write_text("XAI_API_KEY=sk-test-should-not-pass\n", encoding="utf-8")
        with self.assertRaises(ImportRejected):
            import_stage(clean, self.bank)
        if sources.is_dir():
            self.assertEqual(list(sources.iterdir()), [])
        self.assertTrue((self.bank / "quarantine").is_dir())
        self.assertTrue(any((self.bank / "quarantine").iterdir()))

    def test_import_stage_rejects_zip_traversal(self):
        zpath = self.tmp / "bad.zip"
        with zipfile.ZipFile(zpath, "w") as handle:
            handle.writestr("../evil.txt", "x")
        with self.assertRaises(ImportRejected):
            import_stage(zpath, self.bank)
        sources = self.bank / "sources" / "manual"
        if sources.is_dir():
            self.assertEqual(list(sources.iterdir()), [])

    def test_import_stage_accepts_safe_file(self):
        page = self.tmp / "hero.html"
        page.write_text("<section>hero</section>\n", encoding="utf-8")
        report = import_stage(page, self.bank)
        self.assertEqual(report["status"], "ok")
        dest = self.bank / report["path"]
        self.assertTrue((dest / "hero.html").is_file())
        self.assertTrue((dest / "provenance.json").is_file())
        self.assertEqual(report["provenance"]["redistribution"], "local-only")
        self.assertEqual(report["provenance"]["license_evidence"], "unknown")

    def test_uninstall_leaves_design_v2(self):
        self.bank.mkdir()
        keep = self.bank / "keep.txt"
        keep.write_text("stay\n", encoding="utf-8")
        man = self.tmp / ".config" / "opencode" / "bestfriend" / "manifests" / "ownership.json"
        man.parent.mkdir(parents=True, exist_ok=True)
        man.write_text(
            json.dumps(
                {
                    "product": "opencode-bestfriend",
                    "modelInvokedSkills": [],
                    "manualSkills": [],
                    "ownedFiles": [],
                    "ownedMcp": [],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        self.assertEqual(cmd_uninstall(), 0)
        self.assertTrue(keep.is_file())
        self.assertEqual(keep.read_text(encoding="utf-8"), "stay\n")

    def test_shim_resolves_clone_lib(self):
        path = ROOT / "skills" / "impeccable" / "scripts" / "design_v2.py"
        spec = importlib.util.spec_from_file_location("design_v2_shim", path)
        self.assertIsNotNone(spec)
        assert spec is not None and spec.loader is not None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        engine = mod.resolve_engine()
        self.assertTrue((engine / "__init__.py").is_file())
        self.assertEqual(engine.resolve(), (ROOT / "lib" / "design_v2").resolve())

    def test_import_sources_shortlist_cli(self):
        page = self.tmp / "hero.html"
        page.write_text("<section>hero</section>\n", encoding="utf-8")
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(cli_main(["design", "import", str(page), "--provider", "manual"]), 0)
        report = json.loads(buf.getvalue())
        self.assertEqual(report["status"], "ok")
        listed = list_sources(self.bank)
        self.assertEqual(listed["status"], "ok")
        manual = next(row for row in listed["providers"] if row["provider"] == "manual")
        self.assertGreaterEqual(manual["count"], 1)
        hero = _item(
            id="section:cli-hero",
            name="CLI hero",
            description="Dark dense professional hero",
            kind="section",
            tags=["hero", "dark"],
            categories=["hero"],
            dna={"aesthetic": ["dark"], "density": "dense"},
            search_text="cli hero dark dense",
        )
        self._inbox(hero)
        rebuild(self.bank)
        payload = shortlist("dark dense hero", intent="greenfield", mode="Operate")
        self.assertEqual(payload["packages_loaded_during_search"], 0)
        self.assertEqual(payload["offline"], True)
        ids = [row["id"] for row in payload["visuals"]]
        self.assertIn("section:cli-hero", ids)

    def test_grok_skip_fts_alias(self):
        os.environ.pop("OPENCODE_DESIGN_V2_SKIP_FTS", None)
        os.environ["GROK_DESIGN_V2_SKIP_FTS"] = "1"
        rebuild(self.bank)
        lock = json.loads((self.bank / "catalog" / "catalog.lock.json").read_text(encoding="utf-8"))
        self.assertEqual(lock["fts"]["status"], "skipped")

    def test_rebuild_does_not_require_sqlite(self):
        os.environ["OPENCODE_DESIGN_V2_SKIP_FTS"] = "1"
        result = rebuild(self.bank)
        lock = json.loads((self.bank / "catalog" / "catalog.lock.json").read_text(encoding="utf-8"))
        self.assertIsNone(lock["fts"]["sqlite_filename"])
        self.assertTrue((self.bank / "catalog" / lock["jsonl_filename"]).is_file())
        self.assertEqual(result["item_count"], 0)


class HardlinkImportTests(IsolatedHome):
    def setUp(self):
        super().setUp()
        self.bank = self.tmp / "DesignV2"
        os.environ["OPENCODE_DESIGN_V2"] = str(self.bank)

    def tearDown(self):
        os.environ.pop("OPENCODE_DESIGN_V2", None)
        super().tearDown()

    def test_hardlink_rejected(self):
        src = self.tmp / "hl"
        src.mkdir()
        target = src / "a.html"
        target.write_text("<p>a</p>\n", encoding="utf-8")
        link = src / "b.html"
        try:
            os.link(target, link)
        except OSError:
            self.skipTest("hardlinks unsupported")
        if link.lstat().st_nlink < 2:
            self.skipTest("hardlink nlink not visible")
        with self.assertRaises(ImportRejected):
            import_stage(src, self.bank)


if __name__ == "__main__":
    unittest.main()

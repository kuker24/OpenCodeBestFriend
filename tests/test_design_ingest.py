#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.design_v2.importers.common import IngestRejected, copy_tree_filtered  # noqa: E402
from lib.design_v2.importers.open_design import v1_to_v2  # noqa: E402
from lib.design_v2.ingest import ingest_path  # noqa: E402
from lib.design_v2.dedupe import dedupe  # noqa: E402
from lib.design_v2.schema import check_item, empty_item_v1  # noqa: E402
from lib.cli import main as cli_main  # noqa: E402
from tests.support import IsolatedHome  # noqa: E402


class IngestTests(IsolatedHome):
    def setUp(self):
        super().setUp()
        self.bank = self.tmp / "DesignV2"
        os.environ["OPENCODE_DESIGN_V2"] = str(self.bank)

    def tearDown(self):
        os.environ.pop("OPENCODE_DESIGN_V2", None)
        super().tearDown()

    def test_aura_html_design_md(self):
        export = self.tmp / "aura-export"
        export.mkdir()
        (export / "DESIGN.md").write_text("Futuristic dark AI hero\n", encoding="utf-8")
        (export / "index.html").write_text("<section class='hero'>AI</section>\n", encoding="utf-8")
        (export / "styles.css").write_text("body{background:#000}\n", encoding="utf-8")
        result = ingest_path(export, self.bank, provider="aura")
        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["id"].startswith("section:aura-"))
        item = json.loads((self.bank / "inbox" / (result["id"].replace(":", "-") + ".json")).read_text(encoding="utf-8"))
        self.assertEqual(check_item(item), [])
        self.assertEqual(item["license"]["redistribution"], "local-only")
        self.assertEqual(item["source"]["type"], "user-export")
        self.assertTrue((self.bank / item["source"]["local_path"] / "index.html").is_file())

    def test_aura_unknown_layout(self):
        dump = self.tmp / "random"
        dump.mkdir()
        (dump / "notes.txt").write_text("hello\n", encoding="utf-8")
        with self.assertRaises(IngestRejected) as ctx:
            ingest_path(dump, self.bank, provider="aura")
        self.assertIn("UNKNOWN_AURA_LAYOUT", str(ctx.exception))
        sources = self.bank / "sources" / "aura"
        if sources.is_dir():
            self.assertEqual([p for p in sources.iterdir() if p.is_dir()], [])

    def test_normalized_asset_replace_removes_stale_files(self):
        src = self.tmp / "asset"
        src.mkdir()
        (src / "index.html").write_text("<h1>one</h1>\n", encoding="utf-8")
        (src / "old-animation.js").write_text("old\n", encoding="utf-8")
        dest = self.bank / "sections" / "aura" / "hero"
        copy_tree_filtered(src, dest)
        self.assertTrue((dest / "old-animation.js").is_file())
        (src / "old-animation.js").unlink()
        (src / "index.html").write_text("<h1>two</h1>\n", encoding="utf-8")
        copy_tree_filtered(src, dest)
        self.assertFalse((dest / "old-animation.js").exists())
        self.assertEqual((dest / "index.html").read_text(encoding="utf-8"), "<h1>two</h1>\n")

    def test_21st_rejects_scrape_and_media(self):
        scrape = self.tmp / "scrape"
        scrape.mkdir()
        payload = [{"previewUrl": "http://x", "title": f"c{i}"} for i in range(6)]
        (scrape / "dump.json").write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaises(IngestRejected) as ctx:
            ingest_path(scrape, self.bank, provider="21st")
        self.assertIn("MARKETPLACE_SCRAPE_JSON", str(ctx.exception))

        media = self.tmp / "thumbs"
        media.mkdir()
        for i in range(6):
            (media / f"preview-{i}.webp").write_bytes(b"RIFF....WEBP")
        with self.assertRaises(IngestRejected) as ctx:
            ingest_path(media, self.bank, provider="21st")
        self.assertIn("MARKETPLACE_MEDIA_DUMP", str(ctx.exception))

        html = self.tmp / "saved-page"
        html.mkdir()
        (html / "index.html").write_text(
            "<html>Copy prompt 21st.dev/community The living library</html>\n",
            encoding="utf-8",
        )
        with self.assertRaises(IngestRejected) as ctx:
            ingest_path(html, self.bank, provider="21st")
        self.assertIn("MARKETPLACE_HTML", str(ctx.exception))

    def test_21st_user_selected_source(self):
        src = self.tmp / "button"
        src.mkdir()
        (src / "Button.tsx").write_text("export function Button(){return <button/>}\n", encoding="utf-8")
        result = ingest_path(src, self.bank, provider="21st")
        self.assertEqual(result["status"], "ok")
        item = json.loads((self.bank / "inbox" / (result["id"].replace(":", "-") + ".json")).read_text(encoding="utf-8"))
        self.assertEqual(item["provenance"]["marketplace_media_copied"], False)
        self.assertEqual(item["license"]["redistribution"], "local-only")
        self.assertIsNone(item["source"]["canonical_url"])
        self.assertEqual(check_item(item), [])

    def test_open_design_rejects_zip(self):
        zpath = self.tmp / "pack.zip"
        zpath.write_bytes(b"PK\x03\x04")
        with self.assertRaises(IngestRejected) as ctx:
            ingest_path(zpath, self.bank, provider="open-design")
        self.assertIn("OPEN_DESIGN_BANK_REQUIRED", str(ctx.exception))

    def test_open_design_v1_convert(self):
        v1 = empty_item_v1()
        v1["name"] = "Dense dark dashboard"
        v1["description"] = "cyber security ops"
        converted = v1_to_v2(v1)
        self.assertEqual(converted["schema_version"], 2)
        self.assertEqual(converted["source"]["type"], "archive")
        self.assertEqual(converted["provenance"]["acquisition_method"], "open-design-legacy")
        self.assertEqual(converted["license"]["redistribution"], "local-only")
        self.assertEqual(check_item(converted), [])

    def test_bank_pointer_indexes_without_copy(self):
        design = self.tmp / "Design"
        (design / "Refero" / "bank").mkdir(parents=True)
        (design / "motionsites" / "library").mkdir(parents=True)
        (design / "Refero" / "bank" / "catalog.json").write_text(
            json.dumps(
                {
                    "items": [
                        {
                            "name": "Noir Ops",
                            "slug": "noir-ops",
                            "northStar": "dark dense security",
                            "tags": ["dark", "dashboard"],
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        (design / "motionsites" / "library" / "catalog.json").write_text(
            json.dumps({"items": [{"id": "hero-01", "title": "Hero", "jenis": "hero", "types_source": ["hero"]}]}),
            encoding="utf-8",
        )
        result = ingest_path(design, self.bank, provider="refero")
        self.assertEqual(result["copied_media"], False)
        self.assertEqual(result["count"], 2)
        pointer = json.loads((self.bank / "sources" / "refero" / "pointer.json").read_text(encoding="utf-8"))
        self.assertFalse(pointer["copied_media"])
        inbox = list((self.bank / "inbox").glob("*.json"))
        self.assertEqual(len(inbox), 2)

    def test_dedupe_content_hash(self):
        export = self.tmp / "once"
        export.mkdir()
        (export / "DESIGN.md").write_text("Hero\n", encoding="utf-8")
        (export / "index.html").write_text("<section>hero</section>\n", encoding="utf-8")
        first = ingest_path(export, self.bank, provider="aura")
        inbox = self.bank / "inbox"
        original = json.loads((inbox / (first["id"].replace(":", "-") + ".json")).read_text(encoding="utf-8"))
        clone = dict(original)
        clone["id"] = "section:aura-copy"
        clone["canonical_id"] = clone["id"]
        (inbox / "section-aura-copy.json").write_text(json.dumps(clone, indent=2) + "\n", encoding="utf-8")
        report = dedupe(self.bank)
        self.assertGreaterEqual(report["marked"], 1)
        rows = [json.loads(p.read_text(encoding="utf-8")) for p in inbox.glob("*.json")]
        marked = [row for row in rows if row.get("duplicate_of")]
        self.assertEqual(len(marked), 1)
        ids = {first["id"], "section:aura-copy"}
        self.assertIn(marked[0]["id"], ids)
        self.assertIn(marked[0]["duplicate_of"], ids)

    def test_cli_ingest(self):
        export = self.tmp / "cli-aura"
        export.mkdir()
        (export / "index.html").write_text("<h1>Hero</h1>\n", encoding="utf-8")
        (export / "DESIGN.md").write_text("Dark hero\n", encoding="utf-8")
        rc = cli_main(["design", "ingest", str(export), "--provider", "aura", "--bank", str(self.bank)])
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import os
import sys
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "design_v2"
sys.path.insert(0, str(ROOT))

from lib.design_v2.bank import load_policy  # noqa: E402
from lib.design_v2.import_stage import ImportRejected, import_stage  # noqa: E402
from lib.design_v2.importers.common import IngestRejected  # noqa: E402
from lib.design_v2.ingest import ingest_path, ingest_staged  # noqa: E402
from lib.design_v2.provenance import ProvenanceError  # noqa: E402
from lib.design_v2.rebuild import RebuildError, rebuild  # noqa: E402
from lib.design_v2.security import compile_secret_patterns, secret_hits  # noqa: E402
from tests.support import IsolatedHome  # noqa: E402


class DesignV2SecurityTests(IsolatedHome):
    def setUp(self) -> None:
        super().setUp()
        self.bank = self.tmp / "DesignV2"
        os.environ["OPENCODE_DESIGN_V2"] = str(self.bank)

    def tearDown(self) -> None:
        os.environ.pop("OPENCODE_DESIGN_V2", None)
        super().tearDown()

    def test_zip_absolute_windows_and_parent_traversal_are_rejected(self) -> None:
        for index, member in enumerate(("/absolute.txt", "C:\\windows.txt", "folder/../../parent.txt")):
            archive = self.tmp / f"bad-{index}.zip"
            with zipfile.ZipFile(archive, "w") as handle:
                handle.writestr(member, "synthetic")
            with self.subTest(member=member), self.assertRaises(ImportRejected) as raised:
                import_stage(archive, self.bank, provider="manual")
            self.assertIn("zip_traversal", str(raised.exception))

    def test_oversized_file_and_compression_bomb_are_rejected(self) -> None:
        policy = copy.deepcopy(load_policy())
        policy["import"]["max_file_bytes"] = 16
        policy["import"]["max_total_bytes"] = 32
        oversized = self.tmp / "large.html"
        oversized.write_bytes(b"x" * 17)
        with patch("lib.design_v2.import_stage.load_policy", return_value=policy):
            with self.assertRaises(ImportRejected) as raised:
                import_stage(oversized, self.bank, provider="manual")
        self.assertIn("too_large", str(raised.exception))

        bomb = self.tmp / "ratio.zip"
        with zipfile.ZipFile(bomb, "w", compression=zipfile.ZIP_DEFLATED) as handle:
            handle.writestr("payload.html", "A" * 1_000_000)
        with self.assertRaises(ImportRejected) as raised:
            import_stage(bomb, self.bank, provider="manual")
        self.assertIn("zip_ratio", str(raised.exception))

    def test_staged_provenance_and_source_id_fail_closed(self) -> None:
        report = import_stage(FIXTURES / "aura-export", self.bank, provider="aura")
        source = self.bank / report["path"]
        (source / "provenance.json").write_text("[]\n", encoding="utf-8")
        with self.assertRaises(ProvenanceError):
            ingest_staged(self.bank, "aura", report["source_id"])
        with self.assertRaises(IngestRejected) as raised:
            ingest_staged(self.bank, "aura", "../../outside")
        self.assertIn("source_id", str(raised.exception))

    def test_explicit_aura_manifest_fails_closed_when_malformed(self) -> None:
        export = self.tmp / "bad-aura-manifest"
        export.mkdir()
        (export / "index.html").write_text("<main>synthetic</main>\n", encoding="utf-8")
        (export / "design-v2.json").write_text("[]\n", encoding="utf-8")
        with self.assertRaises(IngestRejected) as raised:
            ingest_path(export, self.bank, provider="aura")
        self.assertIn("MALFORMED_AURA_MANIFEST", str(raised.exception))

    def test_credential_patterns_cover_required_secret_classes(self) -> None:
        patterns = compile_secret_patterns(load_policy())
        samples = [
            "AWS_ACCESS_" + "KEY_ID=synthetic-value",
            "AWS_SECRET_ACCESS_" + "KEY=synthetic-value",
            "Bearer " + "synthetic-token-value-1234567890",
            "-----BEGIN " + "OPENSSH PRIVATE KEY-----",
            "DATABASE_" + "URL=mysql://user:password@localhost/db",
            "gh" + "p_" + "x" * 24,
        ]
        self.assertTrue(all(secret_hits(sample, patterns) for sample in samples))

    def test_invalid_catalog_entry_blocks_atomic_rebuild(self) -> None:
        inbox = self.bank / "inbox"
        inbox.mkdir(parents=True)
        (inbox / "invalid.json").write_text(
            json.dumps({"schema_version": 2, "id": "../../invalid"}),
            encoding="utf-8",
        )
        with self.assertRaises(RebuildError):
            rebuild(self.bank)
        self.assertFalse((self.bank / "catalog" / "catalog.lock.json").exists())
        report = json.loads((self.bank / "reports" / "rebuild-failed.json").read_text(encoding="utf-8"))
        self.assertEqual(report["error"], "schema_invalid")


if __name__ == "__main__":
    unittest.main()

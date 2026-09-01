#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT))
from lib.common import product_version  # noqa: E402


class VersionConsistencyTests(unittest.TestCase):
    def test_vendor_product_versions_match_version_file(self):
        ver = product_version()
        self.assertTrue(re.fullmatch(r"\d+\.\d+\.\d+", ver), ver)
        for rel in ("vendor/provenance.json", "vendor/license-audit.json", "vendor/sources.json"):
            data = json.loads((ROOT / rel).read_text(encoding="utf-8"))
            self.assertEqual(data["productVersion"], ver, rel)

    def test_changelog_mentions_version(self):
        text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn(f"## {product_version()}", text)


if __name__ == "__main__":
    unittest.main()

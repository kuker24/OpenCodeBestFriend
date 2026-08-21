#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT))
from lib.common import load_policy, product_version  # noqa: E402

UNKNOWN = {
    "browser-act",
    "chrome-devtools-axi",
    "emil-design-eng",
    "found-this-design",
    "full-audit-keamanan",
    "full-performance-audit",
    "gh-axi",
    "scroll-world",
    "visual-studio",
}


class LicenseAuditTests(unittest.TestCase):
    def test_every_skill_is_audited(self):
        allow, _, _, _ = load_policy(ROOT)
        audit = json.loads((ROOT / "vendor" / "license-audit.json").read_text(encoding="utf-8"))
        self.assertEqual(set(allow), set(audit["skills"]))
        unknown = {k for k, v in audit["skills"].items() if v.get("redistribution") == "unknown"}
        self.assertEqual(unknown, UNKNOWN)
        for name in unknown:
            self.assertEqual(audit["skills"][name]["license"], "not-stated-in-frontmatter")

    def test_provenance_version_matches_product(self):
        prov = json.loads((ROOT / "vendor" / "provenance.json").read_text(encoding="utf-8"))
        self.assertEqual(prov["productVersion"], product_version())
        self.assertEqual(product_version(), "1.0.4")
        names = {c["component"] for c in prov["components"]}
        self.assertNotIn("other-user-skills", names)
        self.assertTrue(UNKNOWN <= names)


if __name__ == "__main__":
    unittest.main()

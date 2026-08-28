#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT))
from lib.common import product_version, write_json  # noqa: E402
from lib.identity import EXPECTED_PRODUCT, EXPECTED_REPO, identity_findings, load_ownership  # noqa: E402
from tests.support import IsolatedHome  # noqa: E402


class IdentityTests(IsolatedHome):
    def _write_man(self, payload: dict) -> None:
        path = self.tmp / ".config" / "opencode" / "bestfriend" / "manifests" / "ownership.json"
        write_json(path, payload)

    def test_missing_manifest(self):
        rows = identity_findings("1.0.5")
        statuses = {label: status for status, label, _ in rows}
        self.assertEqual(statuses["INSTALLED_PRODUCT"], "FAIL")
        self.assertEqual(statuses["INSTALLED_VERSION"], "FAIL")
        self.assertEqual(statuses["SOURCE_REPOSITORY"], "FAIL")

    def test_malformed_manifest(self):
        path = self.tmp / ".config" / "opencode" / "bestfriend" / "manifests" / "ownership.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{not json", encoding="utf-8")
        rows = identity_findings("1.0.5")
        self.assertTrue(any(s == "FAIL" and l == "INSTALLED_PRODUCT" for s, l, _ in rows))
        loaded = load_ownership()
        self.assertTrue(loaded is not None and loaded.get("__malformed"))

    def test_wrong_product(self):
        self._write_man(
            {
                "product": "ClaudeBestFriend",
                "productVersion": "1.0.5",
                "sourceRepository": EXPECTED_REPO,
            }
        )
        rows = identity_findings("1.0.5")
        ev = [e for s, l, e in rows if l == "INSTALLED_PRODUCT"][0]
        self.assertIn("expected=opencode-bestfriend", ev)
        self.assertIn("actual=ClaudeBestFriend", ev)

    def test_wrong_version(self):
        self._write_man(
            {
                "product": EXPECTED_PRODUCT,
                "productVersion": "1.0.4",
                "sourceRepository": EXPECTED_REPO,
            }
        )
        rows = identity_findings("1.0.5")
        ev = [e for s, l, e in rows if l == "INSTALLED_VERSION"][0]
        self.assertIn("expected=1.0.5", ev)
        self.assertIn("actual=1.0.4", ev)

    def test_wrong_repository(self):
        self._write_man(
            {
                "product": EXPECTED_PRODUCT,
                "productVersion": "1.0.5",
                "sourceRepository": "https://github.com/kuker24/ClaudeBestFriend",
            }
        )
        rows = identity_findings("1.0.5")
        self.assertEqual([s for s, l, _ in rows if l == "SOURCE_REPOSITORY"][0], "FAIL")

    def test_correct_manifest(self):
        ver = product_version()
        self._write_man(
            {
                "product": EXPECTED_PRODUCT,
                "productVersion": ver,
                "sourceRepository": EXPECTED_REPO,
            }
        )
        rows = identity_findings()
        self.assertTrue(all(s == "PASS" for s, _, _ in rows))


if __name__ == "__main__":
    unittest.main()

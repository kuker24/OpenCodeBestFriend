#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.smartdoc.extract import ExtractError, extract_docx  # noqa: E402
from lib.smartdoc.paths import PathEscape, archive_member_ok, assert_under_root, resolve_smartdoc_root  # noqa: E402
from lib.smartdoc.profiles import create_profile  # noqa: E402
from tests.support import IsolatedHome  # noqa: E402


class SmartDocSecurityTests(IsolatedHome):
    def test_archive_members(self):
        self.assertFalse(archive_member_ok("/etc/passwd"))
        self.assertFalse(archive_member_ok("C:/Windows/evil"))
        self.assertFalse(archive_member_ok("foo/../../etc/passwd"))
        self.assertFalse(archive_member_ok("..\\..\\evil"))
        self.assertTrue(archive_member_ok("word/document.xml"))

    def test_zip_traversal_docx(self):
        path = self.tmp / "trav.docx"
        with zipfile.ZipFile(path, "w") as handle:
            handle.writestr("../escape.txt", "nope")
        with self.assertRaises(ExtractError) as raised:
            extract_docx(path)
        self.assertIn("zip_traversal", str(raised.exception))

    def test_symlink_not_followed_for_persist(self):
        root = resolve_smartdoc_root(home_dir=self.tmp)
        root.mkdir()
        outside = self.tmp / "secret.txt"
        outside.write_text("secret\n", encoding="utf-8")
        link = root / "link-out"
        os.symlink(outside, link)
        with self.assertRaises(PathEscape):
            assert_under_root(root, link)

    def test_profile_name_and_leading_dash_file(self):
        root = self.tmp / "SmartDoc"
        with self.assertRaises(PathEscape):
            create_profile(root, "-bad", [])
        with self.assertRaises(PathEscape):
            create_profile(root, "Has Caps", [])


if __name__ == "__main__":
    unittest.main()

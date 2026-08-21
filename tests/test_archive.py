#!/usr/bin/env python3
from __future__ import annotations

import io
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT))
from lib.install import safe_extract  # noqa: E402


class SafeExtractTests(unittest.TestCase):
    def test_rejects_dotdot(self):
        tmp = Path(tempfile.mkdtemp(prefix="ocbf-tar-"))
        self.addCleanup(lambda: __import__("shutil").rmtree(tmp, ignore_errors=True))
        tarpath = tmp / "evil.tar"
        with tarfile.open(tarpath, "w") as tf:
            info = tarfile.TarInfo(name="../../tmp/ocbf-evil")
            payload = b"nope"
            info.size = len(payload)
            tf.addfile(info, io.BytesIO(payload))
        dest = tmp / "out"
        dest.mkdir()
        with tarfile.open(tarpath, "r") as tf:
            with self.assertRaises(SystemExit):
                safe_extract(tf, dest)
        self.assertEqual(list(dest.iterdir()), [])

    def test_extracts_normal_member(self):
        tmp = Path(tempfile.mkdtemp(prefix="ocbf-tar-"))
        self.addCleanup(lambda: __import__("shutil").rmtree(tmp, ignore_errors=True))
        tarpath = tmp / "ok.tar"
        with tarfile.open(tarpath, "w") as tf:
            info = tarfile.TarInfo(name="hello.txt")
            payload = b"ok\n"
            info.size = len(payload)
            tf.addfile(info, io.BytesIO(payload))
        dest = tmp / "out"
        with tarfile.open(tarpath, "r") as tf:
            safe_extract(tf, dest)
        self.assertEqual((dest / "hello.txt").read_bytes(), b"ok\n")


if __name__ == "__main__":
    unittest.main()

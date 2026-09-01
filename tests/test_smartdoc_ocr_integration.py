#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.smartdoc.capabilities import capability_matrix  # noqa: E402
from lib.smartdoc.doctor import _tiny_mixed_pdf, _tiny_text_pdf, run_doctor  # noqa: E402
from lib.smartdoc.extract import extract_file  # noqa: E402


@unittest.skipUnless(os.environ.get("SMARTDOC_OCR_INTEGRATION") == "1", "real OCR integration job")
class RealOcrIntegrationTests(unittest.TestCase):
    def test_real_native_scan_mixed_and_doctor(self):
        matrix = capability_matrix()
        for capability in ("PDF_READ", "IMAGE_READ", "OCR_IMAGE", "OCR_PDF"):
            self.assertEqual(matrix[capability], "READY", capability)

        with tempfile.TemporaryDirectory(prefix="ocbf-real-ocr-") as raw:
            work = Path(raw)
            native = work / "native.pdf"
            mixed = work / "mixed.pdf"
            scan = work / "scan.pdf"
            _tiny_text_pdf(native)
            _tiny_mixed_pdf(mixed, work)

            from PIL import Image, ImageDraw  # type: ignore

            image = Image.new("RGB", (900, 240))
            ImageDraw.Draw(image).text((40, 80), "REAL OCR SCAN PAGE", fill=(255, 255, 255))
            image.save(scan, "PDF")

            native_result = extract_file(native, ocr="AUTO")
            scan_result = extract_file(scan, ocr="AUTO")
            mixed_result = extract_file(mixed, ocr="AUTO")
            self.assertEqual([r["method"] for r in native_result["page_records"]], ["native_text"])
            self.assertEqual([r["method"] for r in scan_result["page_records"]], ["ocr"])
            self.assertEqual([r["method"] for r in mixed_result["page_records"]], ["native_text", "ocr"])

            doctor = run_doctor(root=work / "SmartDoc")
            self.assertTrue(doctor["ok"])
            mixed_check = next(row for row in doctor["checks"] if row["name"] == "mixed_document")
            self.assertEqual(mixed_check["status"], "PASS")
            self.assertEqual(mixed_check["methods"], ["native_text", "ocr"])


if __name__ == "__main__":
    unittest.main()

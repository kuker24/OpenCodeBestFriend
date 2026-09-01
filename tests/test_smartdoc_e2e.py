#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import os
import sys
import unittest
import zipfile
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.cli import main as cli_main  # noqa: E402
from lib.smartdoc.extract import ExtractError, extract_file  # noqa: E402
from lib.smartdoc.originality import local_similarity_audit  # noqa: E402
from lib.smartdoc.smartbook import ingest, retrieve  # noqa: E402
from tests.support import IsolatedHome  # noqa: E402

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _docx(path: Path, paragraphs: list[str], table: list[list[str]] | None = None) -> None:
    body = "".join(f"<w:p><w:r><w:t>{p}</w:t></w:r></w:p>" for p in paragraphs)
    if table:
        rows = "".join(
            "<w:tr>" + "".join(f"<w:tc><w:p><w:r><w:t>{c}</w:t></w:r></w:p></w:tc>" for c in row) + "</w:tr>"
            for row in table
        )
        body += f"<w:tbl>{rows}</w:tbl>"
    document = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<w:document xmlns:w="{W}"><w:body>{body}</w:body></w:document>'
    )
    with zipfile.ZipFile(path, "w") as handle:
        handle.writestr("word/document.xml", document)
        handle.writestr("[Content_Types].xml", "<Types></Types>")


class SmartDocGoldenE2E(IsolatedHome):
    def test_a_pdf_not_configured_is_explicit(self):
        pdf = self.tmp / "tugas.pdf"
        pdf.write_bytes(b"%PDF-1.1\n%\xe2\xe3\xcf\xd3\ntrailer\n%%EOF\n")
        with patch.dict("sys.modules", {"pypdf": None}):
            with patch("lib.smartdoc.ocr.tesseract_bin", return_value=None):
                with patch("lib.smartdoc.extract.shutil.which", return_value=None):
                    result = extract_file(pdf)
        self.assertEqual(result["status"], "NOT_CONFIGURED")
        self.assertIn(result["capability"], {"PDF_READ", "OCR_ENGINE", "OCR_PDF", "PDF_RASTER_NOT_CONFIGURED"})
        self.assertEqual(result.get("text") or "", "")

    def test_b_docx_tables_and_bullets(self):
        path = self.tmp / "laporan.docx"
        _docx(
            path,
            ["Laporan akhir", "Pendahuluan penelitian"],
            [["No", "Item"], ["1", "Subnetting"]],
        )
        result = extract_file(path)
        self.assertEqual(result["status"], "READY")
        self.assertIn("Laporan akhir", result["text"])
        self.assertEqual(result["tables"][0][1][1], "Subnetting")

    def test_c_scan_does_not_invent_text(self):
        pdf = self.tmp / "scan.pdf"
        pdf.write_bytes(b"%PDF-1.1 scan\n%%EOF\n")
        with patch("lib.smartdoc.ocr.tesseract_bin", return_value=None):
            with patch("lib.smartdoc.extract.shutil.which", return_value=None):
                result = extract_file(pdf)
        self.assertIn(result["status"], {"NOT_CONFIGURED", "READY"})
        self.assertEqual(result.get("text") or "", "")

    def test_d_headingless_retrieve_middle(self):
        root = self.tmp / "SmartDoc"
        pages = ["pembuka " * 40, "arsitektur mikroprosesor dan bus data di tengah buku", "penutup " * 40]
        ingest(root, slug="buku", source_name="buku.txt", text="\f".join(pages))
        hits = retrieve(root, "buku", "arsitektur mikroprosesor bus data")
        self.assertIn("tengah", hits[0]["text"])

    def test_e_named_corpus_audit(self):
        report = local_similarity_audit(
            "laporan pengabdian masyarakat di masjid bersih nyaman",
            [
                {"id": "sumber-1.docx", "text": "data anggaran pengabdian masyarakat masjid"},
                {"id": "sumber-2.docx", "text": "gerakan masjid bersih nyaman pengabdian"},
            ],
        )
        self.assertEqual(report["label"], "Local Similarity Audit")
        self.assertEqual(report["corpus"], ["sumber-1.docx", "sumber-2.docx"])

    def test_f_lock_handwriting_pages(self):
        path = self.tmp / "tugas.docx"
        _docx(path, ["1. Hitung 2^6.", "2. Tabel hasil.", "Rumus host = 2^(32-n)-2."] * 20)
        dest = self.tmp / "out"
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cli_main(
                [
                    "smartdoc",
                    "render",
                    str(path),
                    "--renderer",
                    "handwriting",
                    "--output",
                    str(dest / "jawaban.pdf"),
                    "--json",
                ]
            )
        result = json.loads(buf.getvalue())
        if result.get("status") == "NOT_CONFIGURED":
            self.assertEqual(result.get("capability"), "HANDWRITING")
            return
        self.assertEqual(rc, 0)
        self.assertEqual(result["status"], "READY")
        self.assertGreaterEqual(result["pages"], 2)
        self.assertTrue(Path(result["pdf"]).is_file())

    def test_originality_source_unreadable_does_not_report_zero(self):
        source = self.tmp / "scan.pdf"
        source.write_bytes(b"%PDF-1.1 scan\n%%EOF\n")
        corpus = self.tmp / "corpus.txt"
        corpus.write_text("readable corpus evidence", encoding="utf-8")
        buf = io.StringIO()
        with patch("lib.smartdoc.ocr.tesseract_bin", return_value=None):
            with patch("lib.smartdoc.extract.shutil.which", return_value=None):
                with redirect_stdout(buf):
                    rc = cli_main(["smartdoc", "originality", str(source), "--against", str(corpus), "--json"])
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["status"], "AUDIT_NOT_RUN")
        self.assertNotIn("score", payload)

    def test_originality_unreadable_corpus_is_incomplete_not_zero(self):
        source = self.tmp / "source.txt"
        source.write_text("readable source document with enough words for comparison", encoding="utf-8")
        corpus = self.tmp / "scan.pdf"
        corpus.write_bytes(b"%PDF-1.1 scan\n%%EOF\n")
        buf = io.StringIO()
        with patch("lib.smartdoc.ocr.tesseract_bin", return_value=None):
            with patch("lib.smartdoc.extract.shutil.which", return_value=None):
                with redirect_stdout(buf):
                    rc = cli_main(["smartdoc", "originality", str(source), "--against", str(corpus), "--json"])
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["status"], "CORPUS_INCOMPLETE")
        self.assertNotIn("score", payload)

    def test_originality_partial_source_discloses_coverage(self):
        source = {
            "status": "PARTIAL",
            "format": "pdf",
            "text": "source evidence with enough words for a local similarity comparison",
            "pages": 2,
            "pages_total": 3,
            "pages_ready": 2,
            "pages_failed": [2],
            "warnings": ["OCR_TIMEOUT"],
        }
        corpus = {"status": "READY", "format": "txt", "text": "local similarity comparison evidence"}
        buf = io.StringIO()
        with patch("lib.smartdoc.commands.extract_file", side_effect=[source, corpus]):
            with redirect_stdout(buf):
                rc = cli_main(["smartdoc", "originality", "source.pdf", "--against", "corpus.txt", "--json"])
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["status"], "PARTIAL")
        self.assertEqual(payload["coverage"]["source"]["pages_failed"], [2])

    def test_cli_rejects_invalid_ocr_policy(self):
        with self.assertRaises(SystemExit) as raised:
            cli_main(["smartdoc", "extract", "source.pdf", "--ocr", "SOMETIMES"])
        self.assertEqual(raised.exception.code, 2)

    def test_mixed_pdf_page_records_and_form_feed(self):
        pdf = self.tmp / "mixed.pdf"
        pdf.write_bytes(b"%PDF-1.1\n%%EOF\n")
        strong = "N" * 40

        class Page:
            def __init__(self, text):
                self._text = text

            def extract_text(self):
                return self._text

        class Reader:
            pages = [Page(strong), Page("")]

        fake = type(sys)("pypdf")
        fake.PdfReader = lambda *_a, **_k: Reader()
        raster = self.tmp / "r.png"
        try:
            from PIL import Image  # type: ignore

            Image.new("RGB", (8, 8), "white").save(raster)
        except Exception:
            self.skipTest("pillow")

        def fake_ocr(_path, **_k):
            return {
                "status": "READY",
                "text": "ocr-body",
                "confidence": 90.0,
                "confidence_level": "HIGH",
                "engine": "tesseract",
                "language": "eng",
                "warnings": [],
                "tokens": [],
                "sanitization": {"zero_width": 0, "unicode_tags": 0, "controls": 0},
            }

        with patch.dict("sys.modules", {"pypdf": fake}):
            with patch("lib.smartdoc.extract.raster_pdf_page", return_value=raster):
                with patch("lib.smartdoc.ocr.ocr_image", side_effect=fake_ocr):
                    with patch("lib.smartdoc.ocr.tesseract_bin", return_value="/usr/bin/tesseract"):
                        with patch("lib.smartdoc.ocr.select_languages", return_value=["eng"]):
                            with patch("lib.smartdoc.extract.shutil.which", return_value="/usr/bin/pdftoppm"):
                                result = extract_file(pdf)
        self.assertEqual(result["pages"], 2)
        self.assertIsInstance(result["pages"], int)
        self.assertEqual([r["method"] for r in result["page_records"]], ["native_text", "ocr"])
        self.assertEqual(result["text"], strong + "\f" + "ocr-body")
        book = ingest(self.tmp / "SmartDoc", slug="mixed", source_name="mixed.pdf", text=result["text"])
        self.assertEqual(book["manifest"]["section_count"], 2)

    def test_hostile_zip_fails_closed(self):
        path = self.tmp / "evil.docx"
        with zipfile.ZipFile(path, "w") as handle:
            handle.writestr("../evil.txt", "pwn")
            handle.writestr("word/document.xml", "<w:document/>")
        with self.assertRaises(ExtractError):
            extract_file(path)

    def test_doctor_does_not_leave_temp(self):
        os.environ["OPENCODE_SMARTDOC"] = str(self.tmp / "SmartDoc")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cli_main(["smartdoc", "doctor", "--json"])
        payload = json.loads(buf.getvalue())
        cleanup = next(c for c in payload["checks"] if c["name"] == "temp_cleanup")
        self.assertEqual(cleanup["status"], "PASS")
        self.assertIn(rc, {0, 1})


if __name__ == "__main__":
    unittest.main()

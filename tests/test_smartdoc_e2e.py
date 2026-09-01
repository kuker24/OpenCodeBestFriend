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
from lib.smartdoc.contract import content_lock, goal_lock  # noqa: E402
from lib.smartdoc.extract import ExtractError, extract_file  # noqa: E402
from lib.smartdoc.originality import local_similarity_audit  # noqa: E402
from lib.smartdoc.render import render_handwriting  # noqa: E402
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
            result = extract_file(pdf)
        self.assertEqual(result["status"], "NOT_CONFIGURED")
        self.assertEqual(result["capability"], "PDF_READ")
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
        result = extract_file(pdf)
        if result["status"] == "NOT_CONFIGURED":
            self.assertEqual(result.get("text") or "", "")
            return
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
        extracted = extract_file(path)
        contract = content_lock(
            goal_lock(
                {
                    "intent": "TRANSFORM",
                    "goal": {"description": "Handwriting"},
                    "output": {"format": "pdf"},
                    "language": {"primary": "id"},
                }
            ),
            extracted["text"],
        )
        dest = self.tmp / "out"
        dest.mkdir()
        result = render_handwriting(extracted["text"], dest, "jawaban.pdf", contract=contract)
        if result.get("status") == "NOT_CONFIGURED":
            self.assertEqual(result.get("capability"), "HANDWRITING")
            return
        self.assertEqual(result["status"], "READY")
        self.assertGreaterEqual(result["pages"], 2)

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

#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import stat
import sys
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.cli import main as cli_main  # noqa: E402
from lib.smartdoc.capabilities import capability_matrix  # noqa: E402
from lib.smartdoc.contract import (  # noqa: E402
    ContractError,
    assert_content_unchanged,
    compute_confidence,
    content_lock,
    empty_contract,
    goal_lock,
    source_policy_allows_web,
    validate_contract,
)
from lib.smartdoc.extract import ExtractError, extract_docx, extract_file  # noqa: E402
from lib.smartdoc.manifest import add_item, coverage_complete, missing_required, set_status  # noqa: E402
from lib.smartdoc.originality import contains_forbidden_product_language, local_similarity_audit  # noqa: E402
from lib.smartdoc.paths import (  # noqa: E402
    PathEscape,
    assert_under_root,
    resolve_output_path,
    resolve_smartdoc_root,
    safe_filename,
    write_json_private,
)
from lib.smartdoc.profiles import (  # noqa: E402
    create_profile,
    delete_profile,
    list_profiles,
    select_profile,
    selected_profile,
    update_profile,
)
from lib.smartdoc.sanitize import sanitize_document_text  # noqa: E402
from lib.smartdoc.render import RenderError, render_handwriting  # noqa: E402
from lib.smartdoc.semantic import SemanticRegression, assert_no_regression  # noqa: E402
from tests.support import IsolatedHome  # noqa: E402

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _docx(path: Path, body_xml: str) -> None:
    document = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<w:document xmlns:w="{W}"><w:body>{body_xml}</w:body></w:document>'
    )
    with zipfile.ZipFile(path, "w") as handle:
        handle.writestr("word/document.xml", document)
        handle.writestr("[Content_Types].xml", "<Types></Types>")


class SmartDocPathTests(IsolatedHome):
    def test_root_explicit_then_env_then_home(self):
        explicit = self.tmp / "custom"
        env_root = self.tmp / "from-env"
        os.environ.pop("OPENCODE_SMARTDOC", None)
        self.assertEqual(resolve_smartdoc_root(home_dir=self.tmp), (self.tmp / "SmartDoc").resolve())
        os.environ["OPENCODE_SMARTDOC"] = str(env_root)
        self.assertEqual(resolve_smartdoc_root(home_dir=self.tmp), env_root.resolve())
        self.assertEqual(resolve_smartdoc_root(explicit=str(explicit), home_dir=self.tmp), explicit.resolve())

    def test_persist_rejects_escape(self):
        root = resolve_smartdoc_root(home_dir=self.tmp)
        root.mkdir()
        with self.assertRaises(PathEscape):
            assert_under_root(root, self.tmp / "outside.txt")

    def test_output_collision_and_safe_name(self):
        d = self.tmp / "out"
        d.mkdir()
        first = resolve_output_path(d, "Jawaban.pdf")
        first.write_text("a", encoding="utf-8")
        second = resolve_output_path(d, "Jawaban.pdf")
        self.assertEqual(second.name, "Jawaban-1.pdf")
        self.assertEqual(safe_filename("../etc/passwd"), "passwd")
        self.assertEqual(safe_filename("-leading"), "f-leading")

    def test_private_json_mode(self):
        root = self.tmp / "SmartDoc"
        path = root / "profiles" / "campus.json"
        write_json_private(path, {"ok": True})
        self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)


class SmartDocContractTests(unittest.TestCase):
    def test_high_confidence_when_goal_format_language_present(self):
        c = empty_contract()
        c["goal"] = {"description": "Ringkas menjadi cheat sheet"}
        c["output"] = {"format": "pdf"}
        c["language"] = {"primary": "Indonesian"}
        self.assertEqual(compute_confidence(c), "HIGH")
        self.assertEqual(validate_contract(c), [])

    def test_low_confidence_without_goal(self):
        self.assertEqual(compute_confidence(empty_contract()), "LOW")

    def test_goal_and_content_lock(self):
        c = empty_contract()
        c["intent"] = "ANSWER"
        c["goal"] = {"description": "Answer every question"}
        locked = goal_lock(c)
        self.assertTrue(locked["locks"]["goal"])
        with_content = content_lock(locked, "1. empat")
        assert_content_unchanged(with_content, "1. empat")
        with self.assertRaises(ContractError):
            assert_content_unchanged(with_content, "1. lima")

    def test_no_silent_web(self):
        c = empty_contract()
        self.assertFalse(source_policy_allows_web(c))
        c["source_policy"] = {"attached": True, "smartbook": True, "web": True}
        self.assertTrue(source_policy_allows_web(c))

    def test_invalid_role(self):
        c = empty_contract()
        c["inputs"] = [{"file": "x.pdf", "role": "oracle"}]
        self.assertTrue(any(err.startswith("role:") for err in validate_contract(c)))


class SmartDocProfileTests(IsolatedHome):
    def test_flexible_identity_and_no_default_person(self):
        root = self.tmp / "SmartDoc"
        create_profile(root, "campus", [{"label": "Nama", "value": "Budi"}, {"label": "NIM", "value": "12345"}])
        create_profile(root, "school", [{"label": "Nama", "value": "Siti"}])
        self.assertEqual(list_profiles(root), ["campus", "school"])
        select_profile(root, "campus")
        selected = selected_profile(root)
        self.assertIsNotNone(selected)
        assert selected is not None
        self.assertEqual(selected["identity"][0]["value"], "Budi")
        blob = json.dumps(selected)
        self.assertNotIn("Fahmi", blob)
        self.assertNotIn("Harun", blob)
        update_profile(root, "campus", [{"label": "Nama", "value": "Budi"}, {"label": "Kelas", "value": "2A"}])
        delete_profile(root, "campus")
        self.assertIsNone(selected_profile(root))
        with self.assertRaises(PathEscape):
            create_profile(root, "../escape", [])


class SmartDocSanitizeExtractTests(IsolatedHome):
    def test_zero_width_stripped(self):
        cleaned, rec = sanitize_document_text("ab\u200bcd\U000E0065ef")
        self.assertEqual(cleaned, "abcdef")
        self.assertGreater(rec["zero_width"] + rec["unicode_tags"], 0)

    def test_txt_and_docx(self):
        txt = self.tmp / "note.txt"
        txt.write_text("hello", encoding="utf-8")
        self.assertEqual(extract_file(txt)["text"], "hello")
        docx = self.tmp / "tugas.docx"
        _docx(
            docx,
            "<w:p><w:r><w:t>Soal 1</w:t></w:r></w:p>"
            "<w:tbl><w:tr><w:tc><w:p><w:r><w:t>A</w:t></w:r></w:p></w:tc></w:tr></w:tbl>",
        )
        got = extract_docx(docx)
        self.assertEqual(got["status"], "READY")
        self.assertIn("Soal 1", got["text"])
        self.assertEqual(got["tables"], [[["A"]]])

    def test_docx_dtd_rejected(self):
        path = self.tmp / "evil.docx"
        xml = '<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><w:document xmlns:w="%s"></w:document>' % W
        with zipfile.ZipFile(path, "w") as handle:
            handle.writestr("word/document.xml", xml)
        with self.assertRaises(ExtractError):
            extract_docx(path)


class SmartDocManifestOriginalityTests(unittest.TestCase):
    def test_coverage_and_semantic(self):
        man = add_item({"items": []}, "q1", "1")
        man = add_item(man, "q1a", "1a")
        self.assertFalse(coverage_complete(man))
        man = set_status(man, "q1", "answered")
        self.assertEqual(missing_required(man), ["q1a"])
        man = set_status(man, "q1a", "intentionally_unresolved")
        self.assertTrue(coverage_complete(man))
        assert_no_regression("hasil 12 kg pada 2024-01-02 [1]", "hasil 12 kg pada 2024-01-02 [1]")
        with self.assertRaises(SemanticRegression):
            assert_no_regression("hasil 12 kg", "hasil 13 kg")

    def test_local_similarity_named_corpus_not_turnitin(self):
        report = local_similarity_audit(
            "the quick brown fox jumps over the lazy dog today",
            [{"id": "module.md", "text": "the quick brown fox jumps over the lazy dog today extra"}],
        )
        self.assertEqual(report["label"], "Local Similarity Audit")
        self.assertEqual(report["corpus"], ["module.md"])
        self.assertGreater(report["score"], 0.5)
        self.assertEqual(contains_forbidden_product_language(json.dumps(report)), [])
        self.assertTrue(contains_forbidden_product_language("official Turnitin score 0%"))


class SmartDocCliTests(IsolatedHome):
    def test_doctor_json_smoke(self):
        os.environ["OPENCODE_SMARTDOC"] = str(self.tmp / "SmartDoc")
        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cli_main(["smartdoc", "doctor", "--json"])
        payload = json.loads(buf.getvalue())
        names = [c["name"] for c in payload["checks"]]
        for required in (
            "root_writable",
            "profile_roundtrip",
            "docx_extraction",
            "pypdf_import",
            "pillow_render",
            "pdf_assembly",
            "pdftoppm_post_raster",
            "smartbook_read_write",
            "temp_cleanup",
        ):
            self.assertIn(required, names)
        self.assertIn(rc, {0, 1})
        self.assertTrue(payload["ok"] or any(c["status"] == "FAIL" for c in payload["checks"]))
        pypdf = next(c for c in payload["checks"] if c["name"] == "pypdf_import")
        self.assertIn(pypdf["status"], {"PASS", "NOT_CONFIGURED"})
        if pypdf["status"] == "NOT_CONFIGURED":
            self.assertEqual(pypdf.get("dependency"), "pypdf")
            self.assertFalse(pypdf.get("partial"))
        profile = next(c for c in payload["checks"] if c["name"] == "profile_roundtrip")
        self.assertEqual(profile["status"], "PASS")
        pdftoppm = next(c for c in payload["checks"] if c["name"] == "pdftoppm_post_raster")
        self.assertIn(pdftoppm["status"], {"PASS", "NOT_CONFIGURED"})

    def test_status_matrix(self):
        os.environ["OPENCODE_SMARTDOC"] = str(self.tmp / "SmartDoc")
        rc = cli_main(["smartdoc", "status", "--json"])
        self.assertEqual(rc, 0)
        matrix = capability_matrix()
        self.assertEqual(matrix["TXT_WRITE"], "READY")
        self.assertEqual(matrix["DOCX_READ"], "READY")
        self.assertIn(matrix["OCR"], {"READY", "NOT_CONFIGURED"})
        self.assertIn(matrix["OCR_ENGINE"], {"READY", "NOT_CONFIGURED"})
        self.assertIn(matrix["OCR_IMAGE"], {"READY", "NOT_CONFIGURED"})
        self.assertIn(matrix["OCR_PDF"], {"READY", "NOT_CONFIGURED"})
        self.assertIn(matrix["PDF_READ"], {"READY", "NOT_CONFIGURED"})
        self.assertIn(matrix["HANDWRITING"], {"READY", "NOT_CONFIGURED"})
        self.assertIn(matrix["POST_PDF_RASTER_QA"], {"READY", "NOT_CONFIGURED"})

    def test_renderer_respects_content_lock(self):
        c = empty_contract()
        c["intent"] = "ANSWER"
        c["goal"] = {"description": "Answer"}
        locked = content_lock(goal_lock(c), "locked-body")
        dest = self.tmp / "out"
        dest.mkdir()
        matrix = capability_matrix()
        if matrix["HANDWRITING"] != "READY":
            result = render_handwriting("locked-body", dest, "x.pdf", contract=locked)
            self.assertEqual(result["status"], "NOT_CONFIGURED")
            return
        with self.assertRaises(RenderError):
            render_handwriting("mutated", dest, "x.pdf", contract=locked)
        result = render_handwriting("locked-body", dest, "Jawaban.pdf", contract=locked, seed=7)
        self.assertEqual(result["status"], "READY")
        self.assertTrue(Path(result["pdf"]).is_file())
        self.assertGreaterEqual(len(result["previews"]), 1)
        again = render_handwriting("locked-body", dest, "Jawaban.pdf", contract=locked, seed=7)
        self.assertEqual(Path(again["pdf"]).name, "Jawaban-1.pdf")
        self.assertEqual(Path(result["previews"][0]).read_bytes(), Path(again["previews"][0]).read_bytes())


if __name__ == "__main__":
    unittest.main()

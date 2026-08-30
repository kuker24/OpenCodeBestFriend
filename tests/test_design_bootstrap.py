#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import shutil
import socket
import urllib.request
import zipfile
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from typing import Any
from unittest.mock import patch

from lib.design_v2.bootstrap import (
    BootstrapError,
    bootstrap_design_bank,
    google_drive_public_url,
    inspect_bootstrap_zip,
    load_bootstrap_sources,
    parse_checksum,
    validate_design_bank,
)
from lib.design_v2.commands import doctor_rows
from lib.design_v2.inspect import inspect_item
from lib.design_v2.search import search, shortlist
from lib.cli import main as cli_main
from tests.support import IsolatedHome


ARCHIVE_NAME = "OpenCodeBestFriend-DesignBank-v1.zip"


class BootstrapTests(IsolatedHome):
    def setUp(self):
        super().setUp()
        self.target = self.tmp / "Design"
        self.design_v2 = self.tmp / "DesignV2"
        self.cache = self.tmp / "cache"
        self.source_tree = self.tmp / "source-bank"
        self._make_design_bank(self.source_tree)
        self.archive = self.tmp / ARCHIVE_NAME
        self._make_archive(self.archive, self.source_tree)
        self.digest = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        self.checksum = self.tmp / f"{ARCHIVE_NAME}.sha256"
        self.checksum.write_text(f"{self.digest}  {ARCHIVE_NAME}\n", encoding="utf-8")
        self.source_config = self.tmp / "bootstrap-sources.json"
        self._write_source_config(self.digest)
        self.download_calls: list[str] = []

    def _write_source_config(self, digest: str) -> None:
        self.source_config.write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "default": "test",
                    "sources": {
                        "test": {
                            "type": "google-drive-public",
                            "bankVersion": "test",
                            "archiveName": ARCHIVE_NAME,
                            "archiveFileId": "1QCqajqPkSl95Y2PDsyC5o-SkyGD7FyRw",
                            "checksumFileId": "1et1hQHKnkW7wvYYdJGAPeY3IB6jsSw5r",
                            "archiveSha256": digest,
                        }
                    },
                }
            ),
            encoding="utf-8",
        )

    def _make_design_bank(self, root: Path) -> None:
        catalogs = {
            "21st/library/catalog.json": {
                "items": [
                    {
                        "id": "demo--avif-button",
                        "jenis": "button",
                        "title": "AVIF Button",
                        "preview": "preview.avif",
                    }
                ]
            },
            "aura/library/catalog.json": {
                "items": [
                    {
                        "id": "aura-hero",
                        "jenis": "hero",
                        "title": "Aura Hero",
                        "preview": "preview.png",
                    }
                ]
            },
            "Refero/bank/catalog.json": {"items": [{"slug": "refero-one", "name": "Refero One"}]},
            "motionsites/library/catalog.json": {
                "items": [{"id": "motion-one", "title": "Motion One", "jenis": "hero"}]
            },
        }
        for relative, payload in catalogs.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload), encoding="utf-8")
        avif = root / "21st/library/button/demo--avif-button/preview.avif"
        avif.parent.mkdir(parents=True)
        avif.write_bytes(b"tiny-avif-fixture")
        aura = root / "aura/library/hero/aura-hero/preview.png"
        aura.parent.mkdir(parents=True)
        aura.write_bytes(b"tiny-png-fixture")

    def _make_archive(self, destination: Path, root: Path, *, prefix: str = "Design") -> None:
        with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, allowZip64=True) as handle:
            for path in sorted(root.rglob("*")):
                if path.is_file():
                    handle.write(path, f"{prefix}/{path.relative_to(root).as_posix()}")

    def _downloader(self, url: str, destination: Path) -> None:
        self.download_calls.append(url)
        source = self.checksum if "1et1hQHKnkW7wvYYdJGAPeY3IB6jsSw5r" in url else self.archive
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    def _bootstrap(self, **kwargs: Any) -> dict:
        return bootstrap_design_bank(
            target=self.target,
            design_v2_root=self.design_v2,
            cache_dir=self.cache,
            downloader=self._downloader,
            config_path=self.source_config,
            **kwargs,
        )

    def test_source_configuration_and_google_drive_endpoint(self):
        default, sources = load_bootstrap_sources()
        self.assertEqual(default, "personal-google-drive-v1")
        source = sources[default]
        self.assertEqual(source.archive_file_id, "1QCqajqPkSl95Y2PDsyC5o-SkyGD7FyRw")
        self.assertEqual(source.checksum_file_id, "1et1hQHKnkW7wvYYdJGAPeY3IB6jsSw5r")
        self.assertEqual(
            source.pinned_sha256,
            "1341c8480d16a579e7d35009287ea5b269ec22da35f9f4f34be6a4571cd6771f",
        )
        url = google_drive_public_url(source.archive_file_id)
        self.assertEqual(url.split("?", 1)[0], "https://drive.usercontent.google.com/download")
        self.assertIn("export=download", url)
        self.assertNotIn("/view", url)

    def test_cli_exposes_bootstrap_dry_run(self):
        output = StringIO()
        with redirect_stdout(output):
            result = cli_main(
                [
                    "design",
                    "bootstrap",
                    "--dry-run",
                    "--target",
                    str(self.target),
                    "--bank",
                    str(self.design_v2),
                    "--json",
                ]
            )
        self.assertEqual(result, 0)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["status"], "dry_run")
        self.assertEqual(payload["target"], str(self.target))

    def test_malformed_source_configuration_is_rejected(self):
        config = self.tmp / "sources.json"
        config.write_text('{"schemaVersion":1,"default":"missing","sources":{}}', encoding="utf-8")
        with self.assertRaises(BootstrapError) as caught:
            load_bootstrap_sources(config)
        self.assertEqual(caught.exception.code, "BOOTSTRAP_SOURCE_INVALID")

    def test_checksum_parser_is_strict(self):
        self.assertEqual(parse_checksum(f"{self.digest} *{ARCHIVE_NAME}\n", ARCHIVE_NAME), self.digest)
        with self.assertRaises(BootstrapError):
            parse_checksum(f"{self.digest}  other.zip\n", ARCHIVE_NAME)
        with self.assertRaises(BootstrapError):
            parse_checksum(f"{self.digest}  {ARCHIVE_NAME}\n{'0' * 64}  {ARCHIVE_NAME}\n", ARCHIVE_NAME)

    def test_checksum_mismatch_fails_closed_before_extraction(self):
        self.checksum.write_text(f"{'0' * 64}  {ARCHIVE_NAME}\n", encoding="utf-8")
        with self.assertRaises(BootstrapError) as caught:
            self._bootstrap()
        self.assertEqual(caught.exception.code, "CHECKSUM_MISMATCH")
        self.assertFalse(self.target.exists())
        self.assertFalse((self.cache / ARCHIVE_NAME).exists())

    def test_html_download_cannot_pass_as_zip(self):
        self.archive.write_text("<html>Google Drive error</html>", encoding="utf-8")
        digest = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        self.checksum.write_text(f"{digest}  {ARCHIVE_NAME}\n", encoding="utf-8")
        self._write_source_config(digest)
        with self.assertRaises(BootstrapError) as caught:
            self._bootstrap()
        self.assertEqual(caught.exception.code, "ARCHIVE_INVALID")
        self.assertFalse(self.target.exists())

    def test_zip_traversal_is_rejected(self):
        with zipfile.ZipFile(self.archive, "w") as handle:
            handle.writestr("../escape.txt", "escape")
        digest = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        self.checksum.write_text(f"{digest}  {ARCHIVE_NAME}\n", encoding="utf-8")
        self._write_source_config(digest)
        with self.assertRaises(BootstrapError) as caught:
            self._bootstrap()
        self.assertEqual(caught.exception.code, "ARCHIVE_UNSAFE")
        self.assertFalse((self.tmp / "escape.txt").exists())

    def test_nested_design_archive_is_normalized_and_bootstrapped(self):
        payload = self._bootstrap()
        self.assertEqual(payload["status"], "ok")
        self.assertTrue((self.target / "21st/library/catalog.json").is_file())
        self.assertFalse((self.target / "Design").exists())
        self.assertEqual(payload["bank"]["counts"], {"21st": 1, "aura": 1, "refero": 1, "motionsites": 1})
        self.assertEqual(payload["population"]["cards"], 4)
        self.assertEqual(payload["population"]["media_copied"], 0)
        self.assertEqual(payload["population"]["broken_pointers"], 0)
        self.assertEqual(payload["population"]["fts"]["schema_version"], 3)
        self.assertFalse(any(path.suffix in {".avif", ".png", ".webp", ".jpg"} for path in self.design_v2.rglob("*")))
        self.assertFalse((self.cache / ARCHIVE_NAME).exists())

    def test_missing_required_catalog_is_rejected_before_commit(self):
        (self.source_tree / "aura/library/catalog.json").unlink()
        self._make_archive(self.archive, self.source_tree)
        digest = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        self.checksum.write_text(f"{digest}  {ARCHIVE_NAME}\n", encoding="utf-8")
        self._write_source_config(digest)
        with self.assertRaises(BootstrapError) as caught:
            self._bootstrap()
        self.assertEqual(caught.exception.code, "DESIGN_BANK_INVALID")
        self.assertFalse(self.target.exists())

    def test_existing_invalid_bank_is_not_overwritten_or_downloaded(self):
        self.target.mkdir()
        sentinel = self.target / "user.txt"
        sentinel.write_text("keep", encoding="utf-8")
        with self.assertRaises(BootstrapError) as caught:
            self._bootstrap()
        self.assertEqual(caught.exception.code, "TARGET_EXISTS")
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")
        self.assertEqual(self.download_calls, [])

    def test_population_failure_reports_the_exact_stage(self):
        shutil.copytree(self.source_tree, self.target)
        with patch("lib.design_v2.bootstrap.rebuild", side_effect=RuntimeError("rebuild boom")):
            with self.assertRaises(BootstrapError) as caught:
                self._bootstrap()
        self.assertEqual(caught.exception.stage, "REBUILT")
        self.assertEqual(caught.exception.code, "REBUILD_FAILED")
        self.assertTrue((self.target / "21st/library/catalog.json").is_file())

    def test_bootstrap_is_idempotent_and_avif_traceable(self):
        first = self._bootstrap()
        calls = len(self.download_calls)
        second = self._bootstrap()
        self.assertEqual(first["status"], "ok")
        self.assertEqual(second["status"], "already_present")
        self.assertEqual(len(self.download_calls), calls)
        self.assertEqual(len(list((self.design_v2 / "inbox").glob("*.json"))), 4)
        item = inspect_item("component:21st-demo-avif-button", root=self.design_v2)
        self.assertEqual(item["preview_status"], "available")
        self.assertTrue(str(item["preview_path"]).endswith("preview.avif"))
        self.assertEqual(second["population"]["dedupe"]["marked"], 0)

    def test_dry_run_and_download_only_have_bounded_effects(self):
        dry = self._bootstrap(dry_run=True)
        self.assertEqual(dry["status"], "dry_run")
        self.assertEqual(self.download_calls, [])
        self.assertFalse(self.target.exists())
        downloaded = self._bootstrap(download_only=True)
        self.assertEqual(downloaded["status"], "downloaded")
        self.assertTrue(Path(downloaded["archive"]).is_file())
        self.assertFalse(self.target.exists())
        self.assertFalse(self.design_v2.exists())

    def test_offline_retrieval_and_doctor_after_bootstrap(self):
        self._bootstrap()

        def network_forbidden(*_args: object, **_kwargs: object) -> None:
            raise AssertionError("offline operation attempted network access")

        with (
            patch.object(socket, "socket", side_effect=network_forbidden),
            patch.object(socket, "create_connection", side_effect=network_forbidden),
            patch.object(urllib.request, "urlopen", side_effect=network_forbidden),
        ):
            result = search("modern button", root=self.design_v2)
            short = shortlist("modern button", root=self.design_v2)
            inspected = inspect_item(result["results"][0]["id"], root=self.design_v2)
            rows = doctor_rows(self.design_v2)
        self.assertEqual(result["bank_status"], "ok")
        self.assertEqual(short["status"], "ok")
        self.assertNotIn("error", inspected)
        self.assertFalse(any(status == "FAIL" for status, _label, _evidence in rows))

    def test_archive_inspection_and_bank_validation_are_bounded(self):
        archive = inspect_bootstrap_zip(self.archive)
        bank = validate_design_bank(self.source_tree)
        self.assertEqual(archive["files"], 6)
        self.assertEqual(bank["preview_samples"]["21st"], 1)
        self.assertEqual(bank["preview_samples"]["aura"], 1)


if __name__ == "__main__":
    import unittest

    unittest.main()

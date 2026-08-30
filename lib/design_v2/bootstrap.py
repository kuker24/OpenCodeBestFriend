from __future__ import annotations

import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
import zipfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from ..common import bf_dir, home, sha256_file, share_dir, write_json
from . import FTS_SCHEMA_VERSION, PACKAGE_DIR
from .bank import DesignV2Error, resolve_design_v2_root
from .commands import bank_health, doctor_rows
from .dedupe import dedupe
from .importers.bank_pointer import (
    POINTER_PREVIEW_SAMPLE,
    pointer_catalog_rows,
    preview_relative_path,
    resolve_catalog_file,
)
from .ingest import ingest_path
from .rebuild import rebuild
from .security import member_ok


SOURCE_CONFIG = PACKAGE_DIR / "bootstrap_sources.json"
SOURCE_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
DRIVE_FILE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{10,128}$")
SHA256_RE = re.compile(r"^([0-9A-Fa-f]{64})[ \t]+\*?([^\r\n]+)$")
ZIP_MAGIC = (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")
BOOTSTRAP_ZIP_LIMITS = {
    "max_members": 150_000,
    "max_member_uncompressed": 1 << 30,
    "max_total_uncompressed": 8 << 30,
    "max_compression_ratio": 500.0,
    "max_path_depth": 24,
    "max_path_length": 512,
}
REQUIRED_CATALOGS = {
    "21st": Path("21st/library/catalog.json"),
    "aura": Path("aura/library/catalog.json"),
    "refero": Path("Refero/bank/catalog.json"),
    "motionsites": Path("motionsites/library/catalog.json"),
}

Downloader = Callable[[str, Path], None]
StageReporter = Callable[[str, str], None]


class BootstrapError(DesignV2Error):
    code = "BOOTSTRAP_FAILED"

    def __init__(self, stage: str, message: str, *, code: str = "BOOTSTRAP_FAILED") -> None:
        super().__init__(f"{stage}: {message}", code=code)
        self.stage = stage
        self.detail = message


@dataclass(frozen=True)
class BootstrapSource:
    name: str
    source_type: str
    bank_version: str
    archive_name: str
    archive_file_id: str
    checksum_file_id: str
    pinned_sha256: str | None = None


def _config_error(message: str) -> BootstrapError:
    return BootstrapError("SOURCE_RESOLVED", message, code="BOOTSTRAP_SOURCE_INVALID")


def load_bootstrap_sources(path: Path | None = None) -> tuple[str, dict[str, BootstrapSource]]:
    config_path = path or SOURCE_CONFIG
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise _config_error("source configuration is unreadable") from exc
    if not isinstance(payload, dict) or set(payload) != {"schemaVersion", "default", "sources"}:
        raise _config_error("source configuration shape")
    if payload.get("schemaVersion") != 1:
        raise _config_error("source configuration schema")
    default = payload.get("default")
    raw_sources = payload.get("sources")
    if not isinstance(default, str) or not SOURCE_NAME_RE.fullmatch(default):
        raise _config_error("default source")
    if not isinstance(raw_sources, dict) or not raw_sources:
        raise _config_error("sources")

    sources: dict[str, BootstrapSource] = {}
    required = {
        "type",
        "bankVersion",
        "archiveName",
        "archiveFileId",
        "checksumFileId",
    }
    allowed = required | {"archiveSha256"}
    for name, raw in raw_sources.items():
        if not isinstance(name, str) or not SOURCE_NAME_RE.fullmatch(name) or not isinstance(raw, dict):
            raise _config_error("source entry")
        if not required.issubset(raw) or set(raw) - allowed:
            raise _config_error(f"source fields for {name}")
        source_type = raw.get("type")
        bank_version = raw.get("bankVersion")
        archive_name = raw.get("archiveName")
        archive_file_id = raw.get("archiveFileId")
        checksum_file_id = raw.get("checksumFileId")
        pinned = raw.get("archiveSha256")
        if source_type != "google-drive-public":
            raise _config_error(f"unsupported source type for {name}")
        if not isinstance(bank_version, str) or not bank_version or len(bank_version) > 32:
            raise _config_error(f"bank version for {name}")
        if (
            not isinstance(archive_name, str)
            or Path(archive_name).name != archive_name
            or not archive_name.endswith(".zip")
        ):
            raise _config_error(f"archive name for {name}")
        if not isinstance(archive_file_id, str) or not DRIVE_FILE_ID_RE.fullmatch(archive_file_id):
            raise _config_error(f"archive file ID for {name}")
        if not isinstance(checksum_file_id, str) or not DRIVE_FILE_ID_RE.fullmatch(checksum_file_id):
            raise _config_error(f"checksum file ID for {name}")
        if pinned is not None and (not isinstance(pinned, str) or not re.fullmatch(r"[0-9A-Fa-f]{64}", pinned)):
            raise _config_error(f"pinned checksum for {name}")
        sources[name] = BootstrapSource(
            name=name,
            source_type=source_type,
            bank_version=bank_version,
            archive_name=archive_name,
            archive_file_id=archive_file_id,
            checksum_file_id=checksum_file_id,
            pinned_sha256=pinned.lower() if isinstance(pinned, str) else None,
        )
    if default not in sources:
        raise _config_error("default source is missing")
    return default, sources


def resolve_bootstrap_source(name: str | None = None, *, config_path: Path | None = None) -> BootstrapSource:
    default, sources = load_bootstrap_sources(config_path)
    selected = name or default
    if selected not in sources:
        raise BootstrapError("SOURCE_RESOLVED", f"unknown source {selected}", code="BOOTSTRAP_SOURCE_UNKNOWN")
    return sources[selected]


def google_drive_public_url(file_id: str) -> str:
    if not DRIVE_FILE_ID_RE.fullmatch(file_id):
        raise _config_error("Google Drive file ID")
    query = urlencode({"id": file_id, "export": "download", "confirm": "t"})
    return f"https://drive.usercontent.google.com/download?{query}"


def _curl_download(url: str, destination: Path) -> None:
    curl = shutil.which("curl")
    if not curl:
        raise BootstrapError("PREFLIGHT", "curl is required", code="CURL_MISSING")
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_name(destination.name + ".part")
    command = [
        curl,
        "--fail",
        "--location",
        "--silent",
        "--show-error",
        "--retry",
        "4",
        "--retry-delay",
        "2",
        "--retry-all-errors",
        "--connect-timeout",
        "30",
        "--output",
        str(partial),
        url,
    ]
    if partial.is_file() and partial.stat().st_size:
        command[1:1] = ["--continue-at", "-"]
    try:
        result = subprocess.run(command, capture_output=True, text=True)
    except OSError as exc:
        partial.unlink(missing_ok=True)
        raise BootstrapError("ARCHIVE_DOWNLOADED", type(exc).__name__, code="DOWNLOAD_FAILED") from exc
    if result.returncode != 0 and "--continue-at" in command:
        partial.unlink(missing_ok=True)
        command[1:3] = []
        try:
            result = subprocess.run(command, capture_output=True, text=True)
        except OSError as exc:
            raise BootstrapError("ARCHIVE_DOWNLOADED", type(exc).__name__, code="DOWNLOAD_FAILED") from exc
    if result.returncode != 0:
        detail = (result.stderr or "curl failed").strip().splitlines()[-1]
        raise BootstrapError("ARCHIVE_DOWNLOADED", detail, code="DOWNLOAD_FAILED")
    if partial.is_symlink() or not partial.is_file() or partial.stat().st_size == 0:
        partial.unlink(missing_ok=True)
        raise BootstrapError("ARCHIVE_DOWNLOADED", "empty download", code="DOWNLOAD_FAILED")
    os.replace(partial, destination)


def download_public_file(url: str, destination: Path) -> None:
    _curl_download(url, destination)


def parse_checksum(text: str, archive_name: str) -> str:
    records: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = SHA256_RE.fullmatch(line)
        if not match:
            raise BootstrapError("CHECKSUM_FETCHED", "malformed SHA-256 file", code="CHECKSUM_INVALID")
        filename = match.group(2).strip()
        if filename != archive_name:
            raise BootstrapError("CHECKSUM_FETCHED", "checksum archive name mismatch", code="CHECKSUM_INVALID")
        records.append(match.group(1).lower())
    if not records or len(set(records)) != 1:
        raise BootstrapError("CHECKSUM_FETCHED", "missing or conflicting SHA-256", code="CHECKSUM_INVALID")
    return records[0]


def _zip_error(message: str, code: str = "ARCHIVE_UNSAFE") -> BootstrapError:
    return BootstrapError("ARCHIVE_INSPECTED", message, code=code)


def inspect_bootstrap_zip(path: Path) -> dict[str, int]:
    try:
        with path.open("rb") as handle:
            magic = handle.read(4)
    except OSError as exc:
        raise _zip_error("archive is unreadable", "ARCHIVE_INVALID") from exc
    if not any(magic.startswith(prefix) for prefix in ZIP_MAGIC):
        raise _zip_error("download is not a ZIP archive", "ARCHIVE_INVALID")
    try:
        with zipfile.ZipFile(path) as handle:
            infos = handle.infolist()
    except (OSError, zipfile.BadZipFile) as exc:
        raise _zip_error("invalid ZIP archive", "ARCHIVE_INVALID") from exc
    limits = BOOTSTRAP_ZIP_LIMITS
    if not infos or len(infos) > int(limits["max_members"]):
        raise _zip_error("ZIP member limit")
    seen: set[str] = set()
    total = 0
    files = 0
    for info in infos:
        name = info.filename.replace("\\", "/")
        if "\x00" in name or not member_ok(name):
            raise _zip_error(f"unsafe ZIP path {name}")
        if len(name) > int(limits["max_path_length"]) or len(Path(name).parts) > int(limits["max_path_depth"]):
            raise _zip_error("ZIP path limit")
        normalized = name.rstrip("/")
        if normalized in seen:
            raise _zip_error(f"duplicate ZIP path {normalized}")
        seen.add(normalized)
        mode = info.external_attr >> 16
        file_type = stat.S_IFMT(mode)
        if stat.S_ISLNK(mode) or file_type not in {0, stat.S_IFREG, stat.S_IFDIR}:
            raise _zip_error(f"special ZIP member {name}")
        if info.flag_bits & 0x1:
            raise _zip_error("encrypted ZIP member")
        if info.is_dir() or name.endswith("/"):
            continue
        files += 1
        uncompressed = int(info.file_size)
        compressed = max(int(info.compress_size), 1)
        if uncompressed > int(limits["max_member_uncompressed"]):
            raise _zip_error("ZIP member size limit")
        if uncompressed and uncompressed / compressed > float(limits["max_compression_ratio"]):
            raise _zip_error("ZIP compression ratio limit")
        total += uncompressed
        if total > int(limits["max_total_uncompressed"]):
            raise _zip_error("ZIP total size limit")
    return {"members": len(infos), "files": files, "uncompressed_bytes": total}


def safe_extract_bootstrap_zip(path: Path, destination: Path) -> dict[str, int]:
    stats = inspect_bootstrap_zip(path)
    destination.mkdir(parents=True, exist_ok=False)
    base = destination.resolve()
    try:
        with zipfile.ZipFile(path) as handle:
            for info in handle.infolist():
                name = info.filename.replace("\\", "/")
                target = destination / name.rstrip("/")
                try:
                    target.resolve(strict=False).relative_to(base)
                except (OSError, ValueError) as exc:
                    raise BootstrapError(
                        "EXTRACTED_TO_TEMP", f"unsafe ZIP path {name}", code="ARCHIVE_EXTRACTION_FAILED"
                    ) from exc
                if info.is_dir() or name.endswith("/"):
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                try:
                    with handle.open(info) as reader, target.open("xb") as writer:
                        shutil.copyfileobj(reader, writer, length=1 << 20)
                except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
                    raise BootstrapError(
                        "EXTRACTED_TO_TEMP", f"failed to extract {name}", code="ARCHIVE_EXTRACTION_FAILED"
                    ) from exc
                st = target.lstat()
                if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1 or st.st_size != info.file_size:
                    raise BootstrapError(
                        "EXTRACTED_TO_TEMP", f"unsafe extracted file {name}", code="ARCHIVE_EXTRACTION_FAILED"
                    )
    except BootstrapError:
        raise
    except (OSError, zipfile.BadZipFile) as exc:
        raise BootstrapError("EXTRACTED_TO_TEMP", "ZIP extraction failed", code="ARCHIVE_EXTRACTION_FAILED") from exc
    return stats


def validate_design_bank(root: Path) -> dict[str, Any]:
    if root.is_symlink() or not root.is_dir():
        raise BootstrapError("BANK_VALIDATED", "Design Bank root is not a directory", code="DESIGN_BANK_INVALID")
    counts: dict[str, int] = {}
    sampled: dict[str, int] = {}
    for provider, relative in REQUIRED_CATALOGS.items():
        catalog = root / relative
        if catalog.is_symlink() or not catalog.is_file():
            raise BootstrapError("BANK_VALIDATED", f"missing {relative}", code="DESIGN_BANK_INVALID")
        try:
            payload = json.loads(catalog.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise BootstrapError(
                "BANK_VALIDATED", f"malformed {relative}", code="DESIGN_BANK_INVALID"
            ) from exc
        rows = pointer_catalog_rows(payload, provider)
        if rows is None:
            raise BootstrapError("BANK_VALIDATED", f"invalid {relative}", code="DESIGN_BANK_INVALID")
        counts[provider] = len(rows)
        sampled[provider] = 0
        if provider not in {"21st", "aura"}:
            continue
        provider_root = root / provider
        for row in rows:
            raw_preview = row.get("preview")
            if not isinstance(raw_preview, str) or not raw_preview.strip():
                continue
            preview = preview_relative_path(row)
            if not preview:
                raise BootstrapError(
                    "BANK_VALIDATED", f"invalid {provider} preview pointer", code="DESIGN_BANK_INVALID"
                )
            resolved = resolve_catalog_file(provider_root, preview)
            if resolved is None or resolved.is_symlink() or not resolved.is_file():
                raise BootstrapError(
                    "BANK_VALIDATED", f"missing {provider} preview {preview}", code="DESIGN_BANK_INVALID"
                )
            sampled[provider] += 1
            if sampled[provider] >= POINTER_PREVIEW_SAMPLE:
                break
    return {"counts": counts, "preview_samples": sampled}


def normalize_extracted_bank(extracted: Path) -> Path:
    nested = extracted / "Design"
    candidates = [nested, extracted] if nested.is_dir() else [extracted]
    last_error: BootstrapError | None = None
    for candidate in candidates:
        try:
            validate_design_bank(candidate)
            return candidate
        except BootstrapError as exc:
            last_error = exc
    assert last_error is not None
    raise last_error


def resolve_design_target(explicit: Path | None = None) -> Path:
    if explicit is not None:
        target = explicit.expanduser()
    else:
        canonical = os.environ.get("OPENCODE_DESIGN_BANK")
        if canonical:
            target = Path(canonical).expanduser()
        else:
            target = Path()
            pointer = bf_dir() / "config" / "design-bank.json"
            if pointer.is_file() and not pointer.is_symlink():
                try:
                    payload = json.loads(pointer.read_text(encoding="utf-8"))
                except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                    payload = None
                root = payload.get("root") if isinstance(payload, dict) else None
                if isinstance(root, str) and root:
                    target = Path(root).expanduser()
            if target == Path():
                legacy = os.environ.get("GROK_DESIGN_BANK")
                target = Path(legacy).expanduser() if legacy else home() / "Design"
    target = target.absolute()
    if target in {Path("/"), home().absolute()}:
        raise BootstrapError("PREFLIGHT", "unsafe Design Bank target", code="TARGET_UNSAFE")
    return target


def _write_design_bank_pointer(target: Path, source: BootstrapSource) -> None:
    write_json(
        bf_dir() / "config" / "design-bank.json",
        {
            "root": str(target),
            "catalogs": [str(path) for path in REQUIRED_CATALOGS.values()],
            "source": source.name,
            "bankVersion": source.bank_version,
            "ownership": "user-data",
        },
    )


def _populate_design_v2(
    design_root: Path,
    design_v2_root: Path,
    *,
    skip_rebuild: bool,
    stage: StageReporter,
) -> dict[str, Any]:
    try:
        ingested = [
            ingest_path(design_root, design_v2_root, provider="bank-pointer"),
            ingest_path(design_root / "21st", design_v2_root, provider="21st"),
            ingest_path(design_root / "aura", design_v2_root, provider="aura"),
        ]
        if any(result.get("copied_media") is not False for result in ingested):
            raise BootstrapError("INGESTED", "pointer ingest copied media", code="MEDIA_COPY_DETECTED")
    except BootstrapError:
        raise
    except Exception as exc:
        code = exc.code if isinstance(exc, DesignV2Error) else "INGEST_FAILED"
        raise BootstrapError("INGESTED", str(exc) or type(exc).__name__, code=code) from exc
    ingested_count = sum(int(result.get("count") or 0) for result in ingested)
    stage("INGESTED", str(ingested_count))
    try:
        dedupe_result = dedupe(design_v2_root)
    except Exception as exc:
        code = exc.code if isinstance(exc, DesignV2Error) else "DEDUPE_FAILED"
        raise BootstrapError("DEDUPED", str(exc) or type(exc).__name__, code=code) from exc
    stage("DEDUPED", str(dedupe_result.get("marked", 0)))
    payload: dict[str, Any] = {
        "ingested": ingested,
        "ingested_count": ingested_count,
        "dedupe": dedupe_result,
        "media_copied": 0,
    }
    if skip_rebuild:
        payload["rebuild"] = {"status": "skipped"}
        payload["doctor"] = {"status": "skipped"}
        return payload
    try:
        rebuild_result = rebuild(design_v2_root)
    except Exception as exc:
        code = exc.code if isinstance(exc, DesignV2Error) else "REBUILD_FAILED"
        raise BootstrapError("REBUILT", str(exc) or type(exc).__name__, code=code) from exc
    stage("REBUILT", str(rebuild_result.get("item_count", 0)))
    try:
        rows = doctor_rows(design_v2_root)
        if any(status == "FAIL" for status, _label, _evidence in rows):
            raise BootstrapError("DOCTOR_PASS", "DesignV2 doctor failed", code="DESIGN_V2_DOCTOR_FAILED")
        health = bank_health(design_v2_root)
    except BootstrapError:
        raise
    except Exception as exc:
        code = exc.code if isinstance(exc, DesignV2Error) else "DESIGN_V2_DOCTOR_FAILED"
        raise BootstrapError("DOCTOR_PASS", str(exc) or type(exc).__name__, code=code) from exc
    stage("DOCTOR_PASS", str(health.get("broken_pointers")))
    fts = health.get("fts") if isinstance(health.get("fts"), dict) else {}
    payload.update(
        {
            "rebuild": rebuild_result,
            "doctor": {"status": "pass", "checks": rows},
            "cards": health.get("total_assets"),
            "fts": fts,
            "broken_pointers": health.get("broken_pointers"),
        }
    )
    return payload


def bootstrap_design_bank(
    *,
    source_name: str | None = None,
    target: Path | None = None,
    design_v2_root: Path | None = None,
    dry_run: bool = False,
    download_only: bool = False,
    skip_rebuild: bool = False,
    config_path: Path | None = None,
    cache_dir: Path | None = None,
    downloader: Downloader = download_public_file,
    report: StageReporter | None = None,
) -> dict[str, Any]:
    stages: list[dict[str, str]] = []

    def stage(name: str, evidence: str = "") -> None:
        stages.append({"stage": name, "evidence": evidence})
        if report:
            report(name, evidence)

    stage("PREFLIGHT")
    source = resolve_bootstrap_source(source_name, config_path=config_path)
    design_target = resolve_design_target(target)
    v2_root = design_v2_root or resolve_design_v2_root()
    stage("SOURCE_RESOLVED", source.name)
    if dry_run:
        stage("COMPLETE", "dry-run")
        return {
            "schema_version": 1,
            "action": "bootstrap",
            "status": "dry_run",
            "source": source.name,
            "source_type": source.source_type,
            "target": str(design_target),
            "design_v2_root": str(v2_root),
            "download_method": "curl-google-drive-public",
            "stages": stages,
        }

    existing = False
    validation: dict[str, Any] | None = None
    if design_target.exists() or design_target.is_symlink():
        try:
            validation = validate_design_bank(design_target)
        except BootstrapError as exc:
            raise BootstrapError(
                "PREFLIGHT", "target exists but is not a compatible Design Bank", code="TARGET_EXISTS"
            ) from exc
        existing = True
        stage("BANK_VALIDATED", "already-present")
        stage("BANK_COMMITTED", "already-present")

    cache = cache_dir or share_dir() / "cache" / "design-bootstrap" / source.name
    archive = cache / source.archive_name
    checksum_file = cache / f"{source.archive_name}.sha256"
    archive_stats: dict[str, int] | None = None
    expected: str | None = None
    if not existing or download_only:
        if cache.is_symlink() or (cache.exists() and not cache.is_dir()):
            raise BootstrapError("PREFLIGHT", "bootstrap cache is not a safe directory", code="CACHE_UNSAFE")
        cache.mkdir(parents=True, exist_ok=True)
        if checksum_file.is_symlink():
            checksum_file.unlink()
        if not checksum_file.is_file():
            try:
                downloader(google_drive_public_url(source.checksum_file_id), checksum_file)
            except BootstrapError as exc:
                if exc.stage == "PREFLIGHT":
                    raise
                raise BootstrapError("CHECKSUM_FETCHED", exc.detail, code=exc.code) from exc
            except Exception as exc:
                raise BootstrapError("CHECKSUM_FETCHED", str(exc), code="DOWNLOAD_FAILED") from exc
        try:
            expected = parse_checksum(checksum_file.read_text(encoding="utf-8"), source.archive_name)
        except BootstrapError:
            checksum_file.unlink(missing_ok=True)
            raise
        except (OSError, UnicodeDecodeError) as exc:
            checksum_file.unlink(missing_ok=True)
            raise BootstrapError("CHECKSUM_FETCHED", "checksum is unreadable", code="CHECKSUM_INVALID") from exc
        if source.pinned_sha256 and expected != source.pinned_sha256:
            raise BootstrapError("CHECKSUM_FETCHED", "checksum does not match pinned digest", code="CHECKSUM_MISMATCH")
        stage("CHECKSUM_FETCHED", expected)

        cached_ok = archive.is_file() and not archive.is_symlink() and sha256_file(archive) == expected
        if not cached_ok:
            archive.unlink(missing_ok=True)
            try:
                downloader(google_drive_public_url(source.archive_file_id), archive)
            except BootstrapError:
                raise
            except Exception as exc:
                raise BootstrapError("ARCHIVE_DOWNLOADED", str(exc), code="DOWNLOAD_FAILED") from exc
        stage("ARCHIVE_DOWNLOADED", "cache" if cached_ok else "network")
        actual = sha256_file(archive)
        if actual != expected:
            archive.unlink(missing_ok=True)
            raise BootstrapError("ARCHIVE_VERIFIED", "archive SHA-256 mismatch", code="CHECKSUM_MISMATCH")
        stage("ARCHIVE_VERIFIED", actual)
        try:
            archive_stats = inspect_bootstrap_zip(archive)
        except BootstrapError:
            archive.unlink(missing_ok=True)
            raise
        stage("ARCHIVE_INSPECTED", json.dumps(archive_stats, sort_keys=True, separators=(",", ":")))
        if download_only:
            stage("COMPLETE", "download-only")
            return {
                "schema_version": 1,
                "action": "bootstrap",
                "status": "downloaded",
                "source": source.name,
                "archive": str(archive),
                "sha256": actual,
                "archive_stats": archive_stats,
                "stages": stages,
            }

    if not existing:
        assert expected is not None
        design_target.parent.mkdir(parents=True, exist_ok=True)
        workspace = Path(tempfile.mkdtemp(prefix=".opencode-design-bootstrap-", dir=str(design_target.parent)))
        extracted = workspace / "extract"
        try:
            safe_extract_bootstrap_zip(archive, extracted)
            stage("EXTRACTED_TO_TEMP", str(extracted))
            normalized = normalize_extracted_bank(extracted)
            validation = validate_design_bank(normalized)
            stage("BANK_VALIDATED", json.dumps(validation["counts"], sort_keys=True, separators=(",", ":")))
            if design_target.exists() or design_target.is_symlink():
                raise BootstrapError("BANK_COMMITTED", "target appeared during bootstrap", code="TARGET_EXISTS")
            try:
                os.replace(normalized, design_target)
            except OSError as exc:
                raise BootstrapError("BANK_COMMITTED", type(exc).__name__, code="BANK_COMMIT_FAILED") from exc
            stage("BANK_COMMITTED", str(design_target))
        finally:
            shutil.rmtree(workspace, ignore_errors=True)
    assert validation is not None
    _write_design_bank_pointer(design_target, source)
    if not existing:
        archive.unlink(missing_ok=True)
        checksum_file.unlink(missing_ok=True)
        try:
            cache.rmdir()
        except OSError:
            pass

    population = _populate_design_v2(design_target, v2_root, skip_rebuild=skip_rebuild, stage=stage)
    if skip_rebuild:
        stage("COMPLETE", "skip-rebuild")
    else:
        stage("COMPLETE")
    return {
        "schema_version": 1,
        "action": "bootstrap",
        "status": "already_present" if existing else "ok",
        "source": source.name,
        "target": str(design_target),
        "design_v2_root": str(v2_root),
        "bank": validation,
        "archive_stats": archive_stats,
        "population": population,
        "fts_schema_expected": FTS_SCHEMA_VERSION,
        "stages": stages,
    }

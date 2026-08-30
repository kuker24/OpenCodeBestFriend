from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .bank import load_policy

ID_RE = re.compile(r"^[a-z]+:[a-z0-9]+(?:-[a-z0-9]+)*$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
SPDX_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.+-]{0,63}$")
REL_PATH_RE = re.compile(r"^[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*$")

ITEM_REQUIRED = (
    "schema_version",
    "id",
    "kind",
    "name",
    "description",
    "source",
    "license",
    "trust",
    "evidence_tier",
    "execution_class",
    "style_authority",
    "intent",
    "modes",
    "surfaces",
    "platforms",
    "categories",
    "tags",
    "capabilities_required",
    "provider",
    "search_policy",
    "selection_policy",
    "canonical_id",
    "alias_of",
    "duplicate_of",
    "dedup_reason",
    "untrusted_text",
    "normalization_status",
    "extraction_evidence",
    "warnings",
)
STRING_ARRAYS = (
    "intent",
    "modes",
    "surfaces",
    "platforms",
    "categories",
    "tags",
    "capabilities_required",
    "extraction_evidence",
    "warnings",
)
V1_ROOT = frozenset(
    list(ITEM_REQUIRED) + ["summary", "search_text"]
)
V2_ROOT = V1_ROOT | frozenset(
    {"dna", "role", "frameworks", "anti_slop", "product_fit", "provenance"}
)
V1_SOURCE = frozenset({"archive", "path", "url", "version", "content_sha256"})
V2_SOURCE = V1_SOURCE | frozenset(
    {"provider", "type", "retrieval", "local_path", "canonical_url", "upstream_id"}
)
LICENSE_KEYS = frozenset({"spdx", "status", "redistribution"})
ZERO_SHA = "0" * 64


def _enum(policy: dict[str, Any], key: str) -> list[Any]:
    return list((policy.get("enums") or {}).get(key) or [])


def empty_item_v1() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "id": "system:example",
        "kind": "system",
        "name": "",
        "description": "",
        "source": {
            "archive": "example.zip",
            "path": "systems/example",
            "url": None,
            "version": None,
            "content_sha256": ZERO_SHA,
        },
        "license": {"spdx": None, "status": "unknown", "redistribution": "local-only"},
        "trust": "unknown",
        "evidence_tier": "E0",
        "execution_class": "reference-only",
        "style_authority": "none",
        "intent": [],
        "modes": [],
        "surfaces": [],
        "platforms": [],
        "categories": [],
        "tags": [],
        "capabilities_required": [],
        "provider": None,
        "search_policy": "metadata-only",
        "selection_policy": "never",
        "canonical_id": "system:example",
        "alias_of": None,
        "duplicate_of": None,
        "dedup_reason": None,
        "untrusted_text": True,
        "normalization_status": "partial",
        "extraction_evidence": [],
        "warnings": [],
        "summary": {},
        "search_text": "",
    }


def empty_item_v2() -> dict[str, Any]:
    item = empty_item_v1()
    item["schema_version"] = 2
    item["id"] = "section:example-hero"
    item["kind"] = "section"
    item["canonical_id"] = "section:example-hero"
    item["source"] = {
        "archive": "",
        "path": "sections/manual/example-hero",
        "url": None,
        "version": None,
        "content_sha256": ZERO_SHA,
        "provider": "manual",
        "type": "manual",
        "retrieval": "offline",
        "local_path": "sections/manual/example-hero",
        "canonical_url": None,
        "upstream_id": None,
    }
    item["dna"] = {}
    item["role"] = "hero"
    item["frameworks"] = []
    item["anti_slop"] = []
    item["product_fit"] = []
    item["provenance"] = {
        "obtained": "user-provided",
        "acquisition_method": "local-path",
        "license_evidence": "unknown",
        "redistribution": "local-only",
        "marketplace_metadata_copied": False,
        "marketplace_media_copied": False,
    }
    return item


def check_lock(lock: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(lock, dict):
        return ["lock"]
    if lock.get("schema_version") != 2:
        errors.append("schema_version")
    gid = str(lock.get("generation_id") or "")
    if not re.fullmatch(r"[0-9a-f]{16}", gid):
        errors.append("generation_id")
    if not re.fullmatch(r"catalog-[0-9a-f]+\.jsonl", str(lock.get("jsonl_filename") or "")):
        errors.append("jsonl_filename")
    if not SHA_RE.fullmatch(str(lock.get("jsonl_sha256") or "")):
        errors.append("jsonl_sha256")
    if not lock.get("created_at"):
        errors.append("created_at")
    if not isinstance(lock.get("item_count"), int) or lock["item_count"] < 0:
        errors.append("item_count")
    hashes = lock.get("input_hashes")
    if not isinstance(hashes, dict):
        errors.append("input_hashes")
    else:
        for name, digest in hashes.items():
            if not isinstance(name, str) or not SHA_RE.fullmatch(str(digest)):
                errors.append(f"input_hashes.{name}")
    fts = lock.get("fts")
    if not isinstance(fts, dict):
        errors.append("fts")
    else:
        if fts.get("status") not in {"available", "unavailable", "failed", "skipped"}:
            errors.append("fts.status")
        sqlite_name = fts.get("sqlite_filename")
        sqlite_sha = fts.get("sqlite_sha256")
        if fts.get("status") == "available" and (sqlite_name is None or sqlite_sha is None):
            errors.append("fts.available_metadata")
        if sqlite_name is not None and not re.fullmatch(r"catalog-[0-9a-f]+\.sqlite3", str(sqlite_name)):
            errors.append("fts.sqlite_filename")
        if sqlite_sha is not None and not SHA_RE.fullmatch(str(sqlite_sha)):
            errors.append("fts.sqlite_sha256")
        schema_version = fts.get("schema_version")
        if schema_version is not None and schema_version != 2:
            errors.append("fts.schema_version")
        extra = set(fts) - {"status", "sqlite_filename", "sqlite_sha256", "schema_version"}
        if extra:
            errors.append("fts.additional")
    return errors


def check_item(item: dict[str, Any], policy: dict[str, Any] | None = None) -> list[str]:
    pol = policy if policy is not None else load_policy()
    if not isinstance(item, dict):
        return ["item"]
    errors: list[str] = []
    version = item.get("schema_version")
    if version not in (1, 2) or not isinstance(version, int):
        return ["schema_version"]
    allowed_root = V1_ROOT if version == 1 else V2_ROOT
    for key in item:
        if key not in allowed_root:
            errors.append(f"additional:{key}")
    for key in ITEM_REQUIRED:
        if key not in item:
            errors.append(f"missing {key}")

    kinds = _enum(pol, "kind_v1") if version == 1 else _enum(pol, "kind")

    def enum_ok(field: str, value: Any, enum_key: str | None = None) -> None:
        allowed = kinds if field == "kind" else _enum(pol, enum_key or field)
        if allowed and value not in allowed:
            errors.append(f"{field}={value!r}")

    if not isinstance(item.get("id"), str) or not ID_RE.fullmatch(item["id"]):
        errors.append("id")
    if not isinstance(item.get("name"), str):
        errors.append("name")
    if not isinstance(item.get("description"), str):
        errors.append("description")
    if not isinstance(item.get("canonical_id"), str) or not ID_RE.fullmatch(str(item.get("canonical_id"))):
        errors.append("canonical_id")
    if not isinstance(item.get("untrusted_text"), bool):
        errors.append("untrusted_text")
    if "search_text" in item and not isinstance(item.get("search_text"), str):
        errors.append("search_text")
    if "summary" in item and not isinstance(item.get("summary"), dict):
        errors.append("summary")
    provider = item.get("provider")
    if provider is not None and not isinstance(provider, str):
        errors.append("provider")
    for key in ("alias_of", "duplicate_of"):
        value = item.get(key)
        if value is None:
            continue
        if not isinstance(value, str) or not ID_RE.fullmatch(value):
            errors.append(key)
    enum_ok("kind", item.get("kind"))
    enum_ok("trust", item.get("trust"))
    enum_ok("evidence_tier", item.get("evidence_tier"))
    enum_ok("execution_class", item.get("execution_class"))
    enum_ok("style_authority", item.get("style_authority"))
    enum_ok("search_policy", item.get("search_policy"))
    enum_ok("selection_policy", item.get("selection_policy"))
    enum_ok("normalization_status", item.get("normalization_status"))
    if item.get("dedup_reason") is not None:
        enum_ok("dedup_reason", item.get("dedup_reason"))

    source = item.get("source")
    source_keys = V1_SOURCE if version == 1 else V2_SOURCE
    if not isinstance(source, dict):
        errors.append("source")
    else:
        required_source = V1_SOURCE if version == 1 else frozenset({"content_sha256"})
        for key in required_source:
            if key not in source:
                errors.append(f"source.{key}")
        for key in source:
            if key not in source_keys:
                errors.append(f"source.additional:{key}")
        digest = source.get("content_sha256")
        if not isinstance(digest, str) or not SHA_RE.fullmatch(digest):
            errors.append("content_sha256")
        path = source.get("path")
        if path not in (None, "") and not (isinstance(path, str) and REL_PATH_RE.fullmatch(path) and ".." not in Path(path).parts):
            errors.append("source.path")
        url = source.get("url")
        if url is not None and not isinstance(url, str):
            errors.append("source.url")
        if version == 2:
            if source.get("type") is not None:
                enum_ok("type", source.get("type"), "source_type")
            if source.get("retrieval") is not None:
                enum_ok("retrieval", source.get("retrieval"), "retrieval")
            local_path = source.get("local_path")
            if local_path not in (None, "") and not (
                isinstance(local_path, str) and REL_PATH_RE.fullmatch(local_path) and ".." not in Path(local_path).parts
            ):
                errors.append("source.local_path")

    license_obj = item.get("license")
    if not isinstance(license_obj, dict):
        errors.append("license")
    else:
        for key in LICENSE_KEYS:
            if key not in license_obj:
                errors.append(f"license.{key}")
        for key in license_obj:
            if key not in LICENSE_KEYS:
                errors.append(f"license.additional:{key}")
        enum_ok("status", license_obj.get("status"), "license_status")
        enum_ok("redistribution", license_obj.get("redistribution"), "redistribution")
        spdx = license_obj.get("spdx")
        if spdx is not None and not (isinstance(spdx, str) and SPDX_RE.fullmatch(spdx)):
            errors.append("license.spdx")

    for key in STRING_ARRAYS:
        value = item.get(key)
        if not isinstance(value, list):
            errors.append(key)
        elif any(not isinstance(entry, str) for entry in value):
            errors.append(f"{key}.items")

    if version == 2:
        for key in ("frameworks", "anti_slop", "product_fit"):
            if key in item:
                value = item.get(key)
                if not isinstance(value, list) or any(not isinstance(entry, str) for entry in value):
                    errors.append(key)
        if "dna" in item and not isinstance(item.get("dna"), dict):
            errors.append("dna")
        if "role" in item and item.get("role") is not None and not isinstance(item.get("role"), str):
            errors.append("role")
        if "provenance" in item and not isinstance(item.get("provenance"), dict):
            errors.append("provenance")

    if item.get("runtime_availability") is not None or item.get("available_via") is not None:
        errors.append("host_probe_persisted")
    pointer = item.get("alias_of") or item.get("duplicate_of")
    if pointer and pointer == item.get("id"):
        errors.append("self_pointer")
    return errors


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError("jsonl_row")
        items.append(row)
    return items


def dump_line(item: dict[str, Any]) -> str:
    return json.dumps(item, sort_keys=True, ensure_ascii=False, separators=(",", ":"))

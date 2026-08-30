from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .bank import DesignV2Error

SOURCE_ID_RE = re.compile(r"^[0-9a-f]{16}$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")

DEFAULT_PROVENANCE = {
    "obtained": "user-provided",
    "acquisition_method": "local-path",
    "license_evidence": "unknown",
    "redistribution": "local-only",
    "marketplace_metadata_copied": False,
    "marketplace_media_copied": False,
}


class ProvenanceError(DesignV2Error):
    code = "MALFORMED_PROVENANCE"


def default_provenance(**overrides: Any) -> dict[str, Any]:
    payload = dict(DEFAULT_PROVENANCE)
    payload.update(overrides)
    return payload


def license_from_evidence(spdx: str | None, evidence: str) -> dict[str, Any]:
    if evidence == "unknown" or not spdx:
        return {"spdx": spdx, "status": "unknown", "redistribution": "local-only"}
    if evidence == "signature":
        return {"spdx": spdx, "status": "known", "redistribution": "local-only"}
    return {"spdx": spdx, "status": "declared-only", "redistribution": "local-only"}


def load_provenance(folder: Path, *, expected_provider: str | None = None) -> dict[str, Any]:
    path = folder / "provenance.json"
    if not path.is_file() or path.is_symlink():
        return default_provenance(provider=expected_provider) if expected_provider else default_provenance()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProvenanceError("unreadable") from exc
    if not isinstance(payload, dict):
        raise ProvenanceError("object_required")
    provider = payload.get("provider")
    if expected_provider and provider != expected_provider:
        raise ProvenanceError("provider_mismatch")
    source_id = payload.get("source_id")
    if source_id is not None and (not isinstance(source_id, str) or not SOURCE_ID_RE.fullmatch(source_id)):
        raise ProvenanceError("source_id")
    digest = payload.get("content_sha256")
    if digest is not None and (not isinstance(digest, str) or not SHA_RE.fullmatch(digest)):
        raise ProvenanceError("content_sha256")
    if payload.get("redistribution") not in {"allowed", "local-only", "blocked", "unknown"}:
        raise ProvenanceError("redistribution")
    for key in ("marketplace_metadata_copied", "marketplace_media_copied"):
        if not isinstance(payload.get(key), bool):
            raise ProvenanceError(key)
    return payload

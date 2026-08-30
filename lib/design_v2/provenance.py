from __future__ import annotations

from typing import Any

DEFAULT_PROVENANCE = {
    "obtained": "user-provided",
    "acquisition_method": "local-path",
    "license_evidence": "unknown",
    "redistribution": "local-only",
    "marketplace_metadata_copied": False,
    "marketplace_media_copied": False,
}


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

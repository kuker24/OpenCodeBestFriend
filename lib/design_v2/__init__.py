"""Offline Design Engine V2. JSONL is canonical; FTS5 is optional."""

from __future__ import annotations

__all__ = [
    "ENV_VAR",
    "ENV_VAR_LEGACY",
    "PACKAGE_DIR",
    "SKIP_FTS_VAR",
    "SKIP_FTS_VAR_LEGACY",
]

from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
ENV_VAR = "OPENCODE_DESIGN_V2"
ENV_VAR_LEGACY = "GROK_DESIGN_V2"
SKIP_FTS_VAR = "OPENCODE_DESIGN_V2_SKIP_FTS"
SKIP_FTS_VAR_LEGACY = "GROK_DESIGN_V2_SKIP_FTS"

"""Offline Design Engine V2. JSONL is canonical; FTS5 is optional."""

from __future__ import annotations

__all__ = [
    "ATOMS_SCHEMA",
    "ENV_VAR",
    "ENV_VAR_LEGACY",
    "FTS_SCHEMA_VERSION",
    "PACKAGE_DIR",
    "SKIP_FTS_VAR",
    "SKIP_FTS_VAR_LEGACY",
    "map_intent_to_role",
    "read_atoms",
    "record_atom_pick",
    "write_atoms",
]

from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
FTS_SCHEMA_VERSION = 3
ENV_VAR = "OPENCODE_DESIGN_V2"
ENV_VAR_LEGACY = "GROK_DESIGN_V2"
SKIP_FTS_VAR = "OPENCODE_DESIGN_V2_SKIP_FTS"
SKIP_FTS_VAR_LEGACY = "GROK_DESIGN_V2_SKIP_FTS"

from .atoms import (
    ATOMS_SCHEMA,
    map_intent_to_role,
    read_atoms,
    record_atom_pick,
    write_atoms,
)

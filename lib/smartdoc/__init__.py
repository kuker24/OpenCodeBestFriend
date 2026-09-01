"""SmartDoc / SmartBook deterministic runtime."""

from __future__ import annotations

from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
ENV_VAR = "OPENCODE_SMARTDOC"
DEFAULT_DIRNAME = "SmartDoc"

__all__ = ["DEFAULT_DIRNAME", "ENV_VAR", "PACKAGE_DIR"]

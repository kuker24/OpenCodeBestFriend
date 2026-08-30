"""Design V2 importers. Open Design is a legacy adapter only."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol


class Importer(Protocol):
    name: str

    def inspect(self, path: Path) -> dict[str, Any]: ...

    def ingest(self, path: Path, bank: Path) -> dict[str, Any]: ...

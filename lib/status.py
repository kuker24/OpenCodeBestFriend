from __future__ import annotations

BLOCKING = frozenset({"FAIL", "DRIFT", "STALE", "MISSING"})
STRICT_BLOCKING = frozenset(
    {
        "DEGRADED",
        "DEGRADED_SECURITY",
        "DEGRADED_AUTH_REQUIRED",
        "DEGRADED_DESIGN_BANK",
        "WARN",
    }
)
NONBLOCKING = frozenset(
    {
        "PASS",
        "CONFIGURED",
        "CONNECTED",
        "OPTIONAL_ABSENT",
        "NOT_APPLICABLE",
        "DESIGN_EXCLUSION",
        "INFO",
        "EMPTY",
        "DEGRADED_FTS",
    }
)


def report(status: str, label: str, evidence: str = "") -> None:
    print(f"{status:<22} {label:<28} {evidence}")


class Findings:
    def __init__(self) -> None:
        self.items: list[tuple[str, str, str]] = []

    def add(self, status: str, label: str, evidence: str = "") -> None:
        self.items.append((status, label, evidence))
        report(status, label, evidence)

    def exit_code(self, strict: bool = False) -> int:
        for status, _label, _ev in self.items:
            if status in BLOCKING:
                return 1
            if strict and status in STRICT_BLOCKING:
                return 1
        return 0

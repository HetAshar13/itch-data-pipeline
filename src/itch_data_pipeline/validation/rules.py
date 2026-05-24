from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationFinding:
    rule_name: str
    status: str
    severity: str
    violations: int
    message: str


def placeholder_validation() -> list[ValidationFinding]:
    return [
        ValidationFinding(
            rule_name="placeholder",
            status="not_run",
            severity="info",
            violations=0,
            message="Validation rules are implemented in a later phase.",
        )
    ]

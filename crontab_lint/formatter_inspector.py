"""Formatter for InspectionResult objects."""
from __future__ import annotations

from .inspector import InspectionResult

_CHECK = "\u2713"
_CROSS = "\u2717"


def format_inspection(result: InspectionResult) -> str:
    lines: list[str] = []

    status = _CHECK if result.valid else _CROSS
    lines.append(f"=== Inspection: {result.expression} ===")
    lines.append(f"  Status      : {status} {'valid' if result.valid else 'invalid'}")

    if result.explanation:
        lines.append(f"  Explanation : {result.explanation}")

    if result.fields:
        lines.append("  Fields      :")
        for name, value in result.fields.items():
            lines.append(f"    {name:<14}: {value}")

    lines.append(f"  Score       : {result.score}/100  (grade: {result.grade})")

    if result.next_runs:
        lines.append("  Next runs   :")
        for run in result.next_runs:
            lines.append(f"    - {run}")
    else:
        lines.append("  Next runs   : n/a")

    if result.suggestions:
        lines.append("  Suggestions :")
        for suggestion in result.suggestions:
            lines.append(f"    * {suggestion}")

    return "\n".join(lines)

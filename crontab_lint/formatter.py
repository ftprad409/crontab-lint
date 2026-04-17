"""Format lint results and conflicts for CLI output."""

from typing import List
from .conflict_detector import Conflict


def format_conflicts(conflicts: List[Conflict]) -> str:
    if not conflicts:
        return "No conflicts detected.\n"
    lines = [f"Found {len(conflicts)} conflict(s):\n"]
    for c in conflicts:
        lines.append(f"  [{c.index_a}] {c.expression_a}")
        lines.append(f"  [{c.index_b}] {c.expression_b}")
        lines.append(f"  Reason : {c.reason}")
        lines.append("")
    return "\n".join(lines)


def format_validation_result(expression: str, valid: bool, explanation: str = "") -> str:
    status = "\u2713 VALID" if valid else "\u2717 INVALID"
    lines = [f"{status}  {expression}"]
    if explanation:
        lines.append(f"  {explanation}")
    return "\n".join(lines)


def format_lint_report(results: List[dict], conflicts: List[Conflict]) -> str:
    """Combine validation results and conflict report into a single string."""
    sections = []
    sections.append("=== Validation Results ===")
    for r in results:
        sections.append(
            format_validation_result(r["expression"], r["valid"], r.get("explanation", ""))
        )
    sections.append("")
    sections.append("=== Conflict Detection ===")
    sections.append(format_conflicts(conflicts))
    return "\n".join(sections)

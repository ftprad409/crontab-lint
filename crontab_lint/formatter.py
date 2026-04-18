"""Format output for the crontab-lint CLI."""
from typing import List
from .conflict_detector import Conflict
from .summarizer import CrontabSummary


def format_conflicts(conflicts: List[Conflict]) -> str:
    if not conflicts:
        return "No conflicts detected.\n"
    lines = ["Conflicts detected:"]
    for c in conflicts:
        lines.append(f"  - '{c.expression_a}' overlaps with '{c.expression_b}': {c.reason}")
    return "\n".join(lines) + "\n"


def format_validation_result(expression: str, valid: bool, explanation: str) -> str:
    status = "VALID" if valid else "INVALID"
    return f"[{status}] {expression}\n  {explanation}\n"


def format_lint_report(expressions: List[str], results: list, conflicts: List[Conflict]) -> str:
    sections = ["=== Lint Report ==="]
    for expr, valid, explanation in results:
        sections.append(format_validation_result(expr, valid, explanation).rstrip())
    sections.append("")
    sections.append(format_conflicts(conflicts).rstrip())
    return "\n".join(sections) + "\n"


def format_summary(summary: CrontabSummary) -> str:
    lines = [
        "=== Summary ===",
        f"  Total expressions : {summary.total}",
        f"  Valid             : {summary.valid}",
        f"  Invalid           : {summary.invalid}",
        f"  Conflicts         : {summary.conflict_count}",
    ]
    if summary.invalid_expressions:
        lines.append("  Invalid entries:")
        for expr in summary.invalid_expressions:
            lines.append(f"    - {expr}")
    return "\n".join(lines) + "\n"

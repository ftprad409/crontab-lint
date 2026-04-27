"""Format scorer results for CLI output."""
from __future__ import annotations

from .scorer import ExpressionScore, ScorerResult

_GRADE_COLOUR = {"A": "\033[32m", "B": "\033[36m", "C": "\033[33m", "D": "\033[31m", "F": "\033[35m"}
_RESET = "\033[0m"


def format_score_entry(entry: ExpressionScore) -> str:
    colour = _GRADE_COLOUR.get(entry.grade, "")
    grade_str = f"{colour}[{entry.grade}]{_RESET}"
    if not entry.valid:
        return f"{grade_str}  {entry.expression}  — invalid expression"
    lines = [f"{grade_str}  {entry.expression}  (score: {entry.score})"]
    for reason in entry.reasons:
        lines.append(f"       • {reason}")
    return "\n".join(lines)


def format_score_report(result: ScorerResult) -> str:
    if not result.scores:
        return "No expressions to score."

    sections = ["=== Complexity Score Report ==="]
    for entry in result.scores:
        sections.append(format_score_entry(entry))

    sections.append("")
    sections.append(f"Average score : {result.average_score}")

    highest = result.highest_risk
    if highest:
        sections.append(f"Highest risk  : {highest.expression}  (score: {highest.score}, grade: {highest.grade})")

    return "\n".join(sections)

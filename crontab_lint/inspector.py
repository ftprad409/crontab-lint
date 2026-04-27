"""Inspector: deep-dive analysis of a single cron expression."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import parse, is_valid
from .explainer import explain
from .scheduler import next_run
from .scorer import _grade
from .optimizer import _check_shorthand, _parts


@dataclass
class InspectionResult:
    expression: str
    valid: bool
    explanation: Optional[str]
    next_runs: List[str]
    score: int
    grade: str
    suggestions: List[str]
    fields: dict


def _score_expression(expression: str) -> int:
    """Compute a simple frequency-risk score (0-100)."""
    if not is_valid(expression):
        return 0
    parts = _parts(expression)
    if not parts:
        return 0
    minute, hour = parts[0], parts[1]
    score = 0
    if minute == "*":
        score += 60
    if hour == "*":
        score += 30
    if "/" in minute:
        try:
            step = int(minute.split("/")[1])
            score += max(0, 30 - step)
        except ValueError:
            pass
    return min(score, 100)


def _field_breakdown(expression: str) -> dict:
    """Return a mapping of field name -> raw value."""
    if not is_valid(expression):
        return {}
    parts = expression.strip().split()
    names = ["minute", "hour", "day_of_month", "month", "day_of_week"]
    return {name: parts[i] for i, name in enumerate(names)}


def inspect(expression: str, runs: int = 5) -> InspectionResult:
    """Perform a full inspection of a single cron expression."""
    valid = is_valid(expression)
    explanation = explain(expression) if valid else None

    next_runs: List[str] = []
    if valid:
        from datetime import datetime
        base = datetime.now().replace(second=0, microsecond=0)
        for _ in range(runs):
            nxt = next_run(expression, base)
            if nxt is None:
                break
            next_runs.append(nxt.strftime("%Y-%m-%d %H:%M"))
            base = nxt

    score = _score_expression(expression)
    grade = _grade(score) if valid else "F"

    suggestions: List[str] = []
    if valid:
        parts = _parts(expression)
        if parts:
            shorthand = _check_shorthand(parts)
            if shorthand:
                suggestions.append(f"Consider using shorthand: {shorthand}")

    return InspectionResult(
        expression=expression,
        valid=valid,
        explanation=explanation,
        next_runs=next_runs,
        score=score,
        grade=grade,
        suggestions=suggestions,
        fields=_field_breakdown(expression),
    )

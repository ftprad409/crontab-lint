"""Score crontab expressions by complexity and risk."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .parser import is_valid, parse


@dataclass
class ExpressionScore:
    expression: str
    score: int
    grade: str
    reasons: List[str] = field(default_factory=list)
    valid: bool = True


@dataclass
class ScorerResult:
    scores: List[ExpressionScore] = field(default_factory=list)

    @property
    def average_score(self) -> float:
        valid_scores = [s.score for s in self.scores if s.valid]
        return round(sum(valid_scores) / len(valid_scores), 2) if valid_scores else 0.0

    @property
    def highest_risk(self) -> ExpressionScore | None:
        valid = [s for s in self.scores if s.valid]
        return max(valid, key=lambda s: s.score) if valid else None


def _grade(score: int) -> str:
    if score <= 2:
        return "A"
    if score <= 5:
        return "B"
    if score <= 8:
        return "C"
    return "D"


def _score_expression(expression: str) -> ExpressionScore:
    if not is_valid(expression):
        return ExpressionScore(expression=expression, score=0, grade="F", valid=False,
                               reasons=["Invalid expression"])

    cron = parse(expression)
    score = 0
    reasons: list[str] = []

    fields = [cron.minute, cron.hour, cron.day_of_month, cron.month, cron.day_of_week]
    names = ["minute", "hour", "day-of-month", "month", "day-of-week"]

    for fname, fval in zip(names, fields):
        if fval == "*":
            score += 1
            reasons.append(f"Wildcard in {fname} increases frequency")
        elif "/" in fval:
            score += 1
            reasons.append(f"Step value in {fname}")
        elif "," in fval:
            reasons.append(f"List in {fname}")

    # Heavy penalty: every minute
    if cron.minute == "*" and cron.hour == "*":
        score += 3
        reasons.append("Runs every minute — high frequency risk")

    return ExpressionScore(
        expression=expression,
        score=score,
        grade=_grade(score),
        reasons=reasons,
        valid=True,
    )


def score(lines: List[str]) -> ScorerResult:
    """Score each cron expression in *lines*, skipping comments and blanks."""
    result = ScorerResult()
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        result.scores.append(_score_expression(stripped))
    return result

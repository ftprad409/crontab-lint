"""Summarize a collection of crontab expressions into statistics."""
from dataclasses import dataclass, field
from typing import List
from .parser import parse, is_valid
from .conflict_detector import detect_conflicts


@dataclass
class CrontabSummary:
    total: int = 0
    valid: int = 0
    invalid: int = 0
    conflict_count: int = 0
    invalid_expressions: List[str] = field(default_factory=list)
    conflict_pairs: List[tuple] = field(default_factory=list)


def summarize(expressions: List[str]) -> CrontabSummary:
    """Return a summary of validation and conflict statistics."""
    summary = CrontabSummary(total=len(expressions))
    valid_exprs = []

    for raw in expressions:
        raw = raw.strip()
        if not raw or raw.startswith("#"):
            summary.total -= 1
            continue
        if is_valid(raw):
            summary.valid += 1
            valid_exprs.append(parse(raw))
        else:
            summary.invalid += 1
            summary.invalid_expressions.append(raw)

    conflicts = detect_conflicts(valid_exprs)
    summary.conflict_count = len(conflicts)
    summary.conflict_pairs = [(c.expression_a, c.expression_b) for c in conflicts]

    return summary

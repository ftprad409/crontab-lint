"""Detect conflicts and overlaps between crontab expressions."""

from dataclasses import dataclass
from typing import List, Tuple
from .parser import CronExpression, parse


@dataclass
class Conflict:
    index_a: int
    index_b: int
    expression_a: str
    expression_b: str
    reason: str


def _expand_field(field_str: str, min_val: int, max_val: int) -> set:
    """Expand a cron field string into a set of matching integers."""
    if field_str == "*":
        return set(range(min_val, max_val + 1))
    result = set()
    for part in field_str.split(","):
        if "/" in part:
            base, step = part.split("/")
            step = int(step)
            start = min_val if base == "*" else int(base.split("-")[0])
            end = max_val if base == "*" else (int(base.split("-")[1]) if "-" in base else max_val)
            result.update(range(start, end + 1, step))
        elif "-" in part:
            start, end = part.split("-")
            result.update(range(int(start), int(end) + 1))
        else:
            result.add(int(part))
    return result


def _expressions_overlap(a: CronExpression, b: CronExpression) -> bool:
    """Return True if two cron expressions can fire at the same time."""
    fields = [
        (a.minute, b.minute, 0, 59),
        (a.hour, b.hour, 0, 23),
        (a.day_of_month, b.day_of_month, 1, 31),
        (a.month, b.month, 1, 12),
        (a.day_of_week, b.day_of_week, 0, 6),
    ]
    for fa, fb, lo, hi in fields:
        if not (_expand_field(fa, lo, hi) & _expand_field(fb, lo, hi)):
            return False
    return True


def detect_conflicts(expressions: List[str]) -> List[Conflict]:
    """Given a list of cron expression strings, return all overlapping pairs."""
    parsed = []
    for expr in expressions:
        try:
            parsed.append(parse(expr))
        except ValueError:
            parsed.append(None)

    conflicts = []
    for i in range(len(parsed)):
        for j in range(i + 1, len(parsed)):
            if parsed[i] is None or parsed[j] is None:
                continue
            if _expressions_overlap(parsed[i], parsed[j]):
                conflicts.append(
                    Conflict(
                        index_a=i,
                        index_b=j,
                        expression_a=expressions[i],
                        expression_b=expressions[j],
                        reason="Expressions can fire at the same time",
                    )
                )
    return conflicts

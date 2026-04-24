"""Compute statistics over a collection of crontab expressions."""

from __future__ import annotations

from dataclasses import dataclass, field
from collections import Counter
from typing import List, Dict

from .parser import parse, is_valid
from .grouper import _classify


@dataclass
class CrontabStatistics:
    total: int = 0
    valid: int = 0
    invalid: int = 0
    comment: int = 0
    blank: int = 0
    schedule_distribution: Dict[str, int] = field(default_factory=dict)
    most_common_minute: str = ""
    most_common_hour: str = ""


def _is_comment(line: str) -> bool:
    return line.strip().startswith("#")


def _is_blank(line: str) -> bool:
    return line.strip() == ""


def compute(lines: List[str]) -> CrontabStatistics:
    """Compute statistics from a list of crontab lines."""
    stats = CrontabStatistics()
    minute_counter: Counter = Counter()
    hour_counter: Counter = Counter()
    category_counter: Counter = Counter()

    for line in lines:
        stats.total += 1

        if _is_comment(line):
            stats.comment += 1
            continue

        if _is_blank(line):
            stats.blank += 1
            continue

        if not is_valid(line):
            stats.invalid += 1
            continue

        stats.valid += 1
        expr = parse(line)
        minute_counter[expr.minute] += 1
        hour_counter[expr.hour] += 1
        category = _classify(expr)
        category_counter[category] += 1

    stats.schedule_distribution = dict(category_counter)

    if minute_counter:
        stats.most_common_minute = minute_counter.most_common(1)[0][0]

    if hour_counter:
        stats.most_common_hour = hour_counter.most_common(1)[0][0]

    return stats

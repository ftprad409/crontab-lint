"""Profiler: analyse crontab load distribution across time slots."""

from dataclasses import dataclass, field
from typing import Dict, List

from .parser import parse, is_valid
from .conflict_detector import _expand_field


@dataclass
class CrontabProfile:
    """Aggregated load profile for a set of cron expressions."""

    hourly_load: Dict[int, int] = field(default_factory=lambda: {h: 0 for h in range(24)})
    minutely_load: Dict[int, int] = field(default_factory=lambda: {m: 0 for m in range(60)})
    busiest_hour: int = 0
    busiest_minute: int = 0
    total_expressions: int = 0
    skipped_expressions: int = 0


def _is_comment(line: str) -> bool:
    return line.strip().startswith("#")


def _is_blank(line: str) -> bool:
    return line.strip() == ""


def profile(lines: List[str]) -> CrontabProfile:
    """Compute load distribution for a list of crontab lines."""
    hourly: Dict[int, int] = {h: 0 for h in range(24)}
    minutely: Dict[int, int] = {m: 0 for m in range(60)}
    total = 0
    skipped = 0

    for line in lines:
        if _is_comment(line) or _is_blank(line):
            continue

        raw = line.split("#")[0].strip()
        if not is_valid(raw):
            skipped += 1
            continue

        expr = parse(raw)
        total += 1

        minutes = _expand_field(expr.minute, 0, 59)
        hours = _expand_field(expr.hour, 0, 23)

        for m in minutes:
            minutely[m] += 1
        for h in hours:
            hourly[h] += 1

    busiest_hour = max(hourly, key=lambda h: hourly[h])
    busiest_minute = max(minutely, key=lambda m: minutely[m])

    return CrontabProfile(
        hourly_load=hourly,
        minutely_load=minutely,
        busiest_hour=busiest_hour,
        busiest_minute=busiest_minute,
        total_expressions=total,
        skipped_expressions=skipped,
    )

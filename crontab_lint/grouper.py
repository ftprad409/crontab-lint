"""Groups crontab expressions by their schedule frequency."""

from dataclasses import dataclass, field
from typing import Dict, List
from .parser import parse, is_valid


@dataclass
class CrontabGroup:
    label: str
    expressions: List[str] = field(default_factory=list)


def _classify(expr: str) -> str:
    """Return a frequency label for a valid cron expression."""
    parsed = parse(expr)
    if parsed is None:
        return "invalid"

    minute, hour, dom, month, dow = (
        parsed.minute,
        parsed.hour,
        parsed.day_of_month,
        parsed.month,
        parsed.day_of_week,
    )

    if minute == "*" and hour == "*":
        return "every_minute"
    if hour == "*" and minute != "*":
        return "every_hour"
    if dom == "*" and month == "*" and dow == "*":
        return "daily"
    if dom == "*" and month == "*" and dow != "*":
        return "weekly"
    if dom != "*" and month == "*":
        return "monthly"
    if month != "*":
        return "yearly"
    return "other"


def group(expressions: List[str]) -> Dict[str, CrontabGroup]:
    """Group a list of cron expression strings by frequency label.

    Invalid expressions are placed in the 'invalid' group.
    Returns a dict mapping label -> CrontabGroup.
    """
    groups: Dict[str, CrontabGroup] = {}

    for expr in expressions:
        expr = expr.strip()
        if not expr or expr.startswith("#"):
            continue

        if not is_valid(expr):
            label = "invalid"
        else:
            label = _classify(expr)

        if label not in groups:
            groups[label] = CrontabGroup(label=label)
        groups[label].expressions.append(expr)

    return groups

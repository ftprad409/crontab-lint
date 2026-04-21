"""Sort crontab expressions by various criteria."""

from dataclasses import dataclass, field
from typing import List, Tuple
from .parser import parse, is_valid
from .conflict_detector import _expand_field


SORTABLE_FIELDS = ("minute", "hour", "day", "month", "weekday")


@dataclass
class SortedCrontab:
    entries: List[str]
    skipped: List[str] = field(default_factory=list)


def _min_value(expression: str, field_name: str) -> int:
    """Return the minimum expanded value for a given field in an expression."""
    try:
        expr = parse(expression)
        limits = {
            "minute": (0, 59),
            "hour": (0, 23),
            "day": (1, 31),
            "month": (1, 12),
            "weekday": (0, 6),
        }
        raw = getattr(expr, field_name)
        lo, hi = limits[field_name]
        values = _expand_field(raw, lo, hi)
        return min(values) if values else lo
    except Exception:
        return 0


def _sort_key(expression: str) -> Tuple:
    """Build a sort key tuple from the five cron fields."""
    return tuple(_min_value(expression, f) for f in SORTABLE_FIELDS)


def sort(
    lines: List[str],
    key: str = "schedule",
    reverse: bool = False,
) -> SortedCrontab:
    """Sort valid crontab expressions.

    Args:
        lines: Raw crontab lines (may include comments and blanks).
        key: Sorting strategy. Currently supports ``"schedule"`` (default)
             which sorts by minute, hour, day, month, weekday in order, and
             ``"alpha"`` which sorts lexicographically.
        reverse: If True, sort in descending order.

    Returns:
        A :class:`SortedCrontab` with sorted valid entries and a list of
        skipped lines (comments, blanks, invalid expressions).
    """
    valid: List[str] = []
    skipped: List[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            skipped.append(line)
            continue
        if is_valid(stripped):
            valid.append(stripped)
        else:
            skipped.append(line)

    if key == "alpha":
        sorted_entries = sorted(valid, reverse=reverse)
    else:
        sorted_entries = sorted(valid, key=_sort_key, reverse=reverse)

    return SortedCrontab(entries=sorted_entries, skipped=skipped)

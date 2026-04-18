"""Next-run time calculator for cron expressions."""

from datetime import datetime, timedelta
from typing import Optional
from .parser import parse, is_valid


def _next_value(current: int, values: list[int], wrap: tuple[int, int]) -> tuple[int, bool]:
    """Return (next_value, wrapped) from sorted values list."""
    for v in values:
        if v >= current:
            return v, False
    return values[0], True


def next_run(expression: str, after: Optional[datetime] = None) -> Optional[datetime]:
    """Return the next datetime a cron expression will fire after *after*.

    Returns None if the expression is invalid.
    """
    if not is_valid(expression):
        return None

    expr = parse(expression)
    dt = (after or datetime.now()).replace(second=0, microsecond=0) + timedelta(minutes=1)

    from .conflict_detector import _expand_field
    minutes = sorted(_expand_field(expr.minute, 0, 59))
    hours = sorted(_expand_field(expr.hour, 0, 23))
    days = sorted(_expand_field(expr.day, 1, 31))
    months = sorted(_expand_field(expr.month, 1, 12))
    weekdays = sorted(_expand_field(expr.weekday, 0, 6))

    for _ in range(366 * 24 * 60):  # max search window ~1 year
        if dt.month not in months:
            # advance to next valid month
            next_m, wrapped = _next_value(dt.month, months, (1, 12))
            if wrapped:
                dt = dt.replace(year=dt.year + 1, month=next_m, day=1, hour=0, minute=0)
            else:
                dt = dt.replace(month=next_m, day=1, hour=0, minute=0)
            continue

        if dt.day not in days or dt.weekday() not in weekdays:
            dt += timedelta(days=1)
            dt = dt.replace(hour=0, minute=0)
            continue

        if dt.hour not in hours:
            next_h, wrapped = _next_value(dt.hour, hours, (0, 23))
            if wrapped:
                dt += timedelta(days=1)
                dt = dt.replace(hour=hours[0], minute=minutes[0])
            else:
                dt = dt.replace(hour=next_h, minute=minutes[0])
            continue

        if dt.minute not in minutes:
            next_min, wrapped = _next_value(dt.minute, minutes, (0, 59))
            if wrapped:
                dt += timedelta(hours=1)
                dt = dt.replace(minute=minutes[0])
            else:
                dt = dt.replace(minute=next_min)
            continue

        return dt

    return None

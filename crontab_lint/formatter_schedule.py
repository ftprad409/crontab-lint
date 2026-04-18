"""Formatting helpers for next-run schedule output."""

from datetime import datetime
from typing import Optional


DATETIME_FMT = "%Y-%m-%d %H:%M"


def format_next_run(expression: str, next_dt: Optional[datetime]) -> str:
    """Return a human-readable line showing the next run time."""
    if next_dt is None:
        return f"  {expression!r:40s}  -> (invalid expression)"
    return f"  {expression!r:40s}  -> {next_dt.strftime(DATETIME_FMT)}"


def format_schedule_report(results: list[tuple[str, Optional[datetime]]]) -> str:
    """Return a full schedule report for a list of (expression, next_dt) pairs."""
    lines = ["=" * 60, "Next Scheduled Runs", "=" * 60]
    for expr, dt in results:
        lines.append(format_next_run(expr, dt))
    lines.append("=" * 60)
    return "\n".join(lines)

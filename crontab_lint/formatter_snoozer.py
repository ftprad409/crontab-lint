"""Formatters for snooze results."""
from __future__ import annotations

from typing import List

from .snoozer import SnoozedExpression, SnoozeResult

_DT_FMT = "%Y-%m-%d %H:%M UTC"


def format_snoozed_entry(entry: SnoozedExpression) -> str:
    """Return a single-line description of a snoozed expression."""
    status = "ACTIVE" if entry.is_active else "EXPIRED"
    until = entry.snoozed_until.strftime(_DT_FMT)
    reason_part = f"  # {entry.reason}" if entry.reason else ""
    return f"  [{status}] {entry.expression!r:40s} until {until}{reason_part}"


def format_snooze_result(result: SnoozeResult) -> str:
    """Return a human-readable report for a SnoozeResult."""
    lines: List[str] = ["=== Snooze Report ==="]

    if result.snoozed:
        lines.append(f"\nSnoozed ({result.total_snoozed}):")
        for entry in result.snoozed:
            lines.append(format_snoozed_entry(entry))
    else:
        lines.append("\nNo new expressions snoozed.")

    if result.skipped_already_snoozed:
        lines.append(f"\nAlready snoozed ({len(result.skipped_already_snoozed)}):")
        for expr in result.skipped_already_snoozed:
            lines.append(f"  {expr!r}")

    if result.skipped_invalid:
        lines.append(f"\nSkipped (invalid) ({len(result.skipped_invalid)}):")
        for expr in result.skipped_invalid:
            lines.append(f"  {expr!r}")

    return "\n".join(lines)


def format_active_snoozes(snoozed: List[SnoozedExpression]) -> str:
    """Return a report listing currently active snooze entries."""
    active = [s for s in snoozed if s.is_active]
    if not active:
        return "No active snoozes."
    lines = [f"Active snoozes ({len(active)}):"] + [
        format_snoozed_entry(e) for e in active
    ]
    return "\n".join(lines)

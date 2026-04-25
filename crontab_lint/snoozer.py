"""Snooze/mute cron expressions for a given time window."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from .parser import is_valid


@dataclass
class SnoozedExpression:
    expression: str
    snoozed_until: datetime
    reason: Optional[str] = None

    @property
    def is_active(self) -> bool:
        """Return True if the snooze window is still in effect."""
        return datetime.utcnow() < self.snoozed_until


@dataclass
class SnoozeResult:
    snoozed: List[SnoozedExpression] = field(default_factory=list)
    skipped_invalid: List[str] = field(default_factory=list)
    skipped_already_snoozed: List[str] = field(default_factory=list)

    @property
    def total_snoozed(self) -> int:
        return len(self.snoozed)


def snooze(
    expressions: List[str],
    duration_minutes: int,
    reason: Optional[str] = None,
    existing: Optional[List[SnoozedExpression]] = None,
) -> SnoozeResult:
    """Snooze a list of cron expressions for *duration_minutes* minutes.

    Already-snoozed (still-active) expressions are not re-snoozed.
    Invalid expressions are collected but not snoozed.
    """
    if duration_minutes <= 0:
        raise ValueError("duration_minutes must be a positive integer")

    existing = existing or []
    active_exprs = {s.expression for s in existing if s.is_active}

    result = SnoozeResult()
    until = datetime.utcnow() + timedelta(minutes=duration_minutes)

    for expr in expressions:
        expr = expr.strip()
        if not expr or expr.startswith("#"):
            continue
        if not is_valid(expr):
            result.skipped_invalid.append(expr)
            continue
        if expr in active_exprs:
            result.skipped_already_snoozed.append(expr)
            continue
        result.snoozed.append(SnoozedExpression(expression=expr, snoozed_until=until, reason=reason))

    return result


def active_snoozes(snoozed_list: List[SnoozedExpression]) -> List[SnoozedExpression]:
    """Return only the snooze entries that are still active."""
    return [s for s in snoozed_list if s.is_active]


def lift_snooze(
    expression: str, snoozed_list: List[SnoozedExpression]
) -> List[SnoozedExpression]:
    """Remove all snooze entries for the given expression."""
    return [s for s in snoozed_list if s.expression != expression]

"""comparator.py — Compare two crontab expressions field-by-field.

Provides a structured diff of individual cron fields so users can
understand exactly how two expressions differ (e.g. same schedule but
different day-of-week).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import parse, is_valid


_FIELD_NAMES = ("minute", "hour", "day_of_month", "month", "day_of_week")


@dataclass(frozen=True)
class FieldDiff:
    """Comparison result for a single cron field."""

    name: str
    left: str
    right: str

    @property
    def differs(self) -> bool:
        """Return True when the two field values are not identical."""
        return self.left != self.right


@dataclass
class ComparisonResult:
    """Full comparison between two crontab expression strings."""

    left: str
    right: str
    left_valid: bool
    right_valid: bool
    field_diffs: List[FieldDiff] = field(default_factory=list)

    @property
    def both_valid(self) -> bool:
        """Return True only when both expressions parsed successfully."""
        return self.left_valid and self.right_valid

    @property
    def are_equivalent(self) -> bool:
        """Return True when both expressions are valid and all fields match."""
        return self.both_valid and not any(d.differs for d in self.field_diffs)

    @property
    def differing_fields(self) -> List[FieldDiff]:
        """Return only the fields that differ between the two expressions."""
        return [d for d in self.field_diffs if d.differs]


def compare(left: str, right: str) -> ComparisonResult:
    """Compare *left* and *right* crontab expressions field-by-field.

    Parameters
    ----------
    left:
        The first crontab expression string.
    right:
        The second crontab expression string.

    Returns
    -------
    ComparisonResult
        A structured result containing per-field diffs and validity flags.
        When either expression is invalid the ``field_diffs`` list will be
        empty — callers should check ``both_valid`` before inspecting diffs.
    """
    left_valid = is_valid(left)
    right_valid = is_valid(right)

    result = ComparisonResult(
        left=left,
        right=right,
        left_valid=left_valid,
        right_valid=right_valid,
    )

    if not (left_valid and right_valid):
        return result

    left_expr = parse(left)
    right_expr = parse(right)

    left_parts = [
        left_expr.minute,
        left_expr.hour,
        left_expr.day_of_month,
        left_expr.month,
        left_expr.day_of_week,
    ]
    right_parts = [
        right_expr.minute,
        right_expr.hour,
        right_expr.day_of_month,
        right_expr.month,
        right_expr.day_of_week,
    ]

    for name, lv, rv in zip(_FIELD_NAMES, left_parts, right_parts):
        result.field_diffs.append(FieldDiff(name=name, left=lv, right=rv))

    return result

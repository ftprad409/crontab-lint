"""Pin specific crontab expressions to prevent them from being modified or flagged."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from crontab_lint.parser import is_valid


@dataclass
class PinnedExpression:
    expression: str
    reason: str
    pinned_at: datetime
    pinned_by: str

    def is_pinned(self) -> bool:
        return True


@dataclass
class PinResult:
    pinned: List[PinnedExpression] = field(default_factory=list)
    skipped_invalid: List[str] = field(default_factory=list)
    skipped_already_pinned: List[str] = field(default_factory=list)

    @property
    def total_pinned(self) -> int:
        return len(self.pinned)

    @property
    def total_skipped(self) -> int:
        return len(self.skipped_invalid) + len(self.skipped_already_pinned)


def _is_comment(line: str) -> bool:
    return line.strip().startswith("#")


def _is_blank(line: str) -> bool:
    return line.strip() == ""


def _already_pinned(expression: str, existing: List[PinnedExpression]) -> bool:
    return any(p.expression == expression for p in existing)


def pin(
    expressions: List[str],
    reason: str,
    pinned_by: str = "user",
    existing: Optional[List[PinnedExpression]] = None,
    now: Optional[datetime] = None,
) -> PinResult:
    """Pin a list of crontab expressions with a reason and author."""
    if existing is None:
        existing = []
    if now is None:
        now = datetime.utcnow()

    result = PinResult()

    for raw in expressions:
        line = raw.strip()
        if _is_comment(line) or _is_blank(line):
            continue

        if not is_valid(line):
            result.skipped_invalid.append(line)
            continue

        if _already_pinned(line, existing):
            result.skipped_already_pinned.append(line)
            continue

        result.pinned.append(
            PinnedExpression(
                expression=line,
                reason=reason,
                pinned_at=now,
                pinned_by=pinned_by,
            )
        )

    return result

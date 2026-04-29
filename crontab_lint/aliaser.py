"""Aliaser: assign and resolve human-friendly aliases for cron expressions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from crontab_lint.parser import is_valid


@dataclass
class AliasEntry:
    alias: str
    expression: str
    valid: bool
    comment: str = ""


@dataclass
class AliasResult:
    entries: List[AliasEntry] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    @property
    def total_aliases(self) -> int:
        return len(self.entries)

    @property
    def total_skipped(self) -> int:
        return len(self.skipped)

    def resolve(self, alias: str) -> Optional[AliasEntry]:
        """Return the AliasEntry for the given alias, or None if not found."""
        for entry in self.entries:
            if entry.alias == alias:
                return entry
        return None

    def as_dict(self) -> Dict[str, str]:
        """Return a mapping of alias -> expression."""
        return {e.alias: e.expression for e in self.entries}


def alias(
    pairs: List[tuple],
    *,
    allow_invalid: bool = False,
) -> AliasResult:
    """Create aliases for cron expressions.

    Args:
        pairs: List of (alias_name, expression[, comment]) tuples.
        allow_invalid: When False (default), expressions that fail
            validation are recorded in ``skipped`` instead of ``entries``.

    Returns:
        An :class:`AliasResult` instance.
    """
    result = AliasResult()
    seen_aliases: Dict[str, bool] = {}

    for item in pairs:
        if len(item) == 3:
            alias_name, expression, comment = item
        else:
            alias_name, expression = item
            comment = ""

        expression = expression.strip()
        alias_name = alias_name.strip()

        if not alias_name or not expression:
            result.skipped.append(alias_name or expression)
            continue

        if alias_name in seen_aliases:
            result.skipped.append(alias_name)
            continue

        valid = is_valid(expression)

        if not valid and not allow_invalid:
            result.skipped.append(alias_name)
            continue

        seen_aliases[alias_name] = True
        result.entries.append(
            AliasEntry(alias=alias_name, expression=expression, valid=valid, comment=comment)
        )

    return result

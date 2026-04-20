"""Diff two crontab files and report added, removed, and changed expressions."""

from dataclasses import dataclass, field
from typing import List, Tuple

from crontab_lint.parser import parse, is_valid


@dataclass
class CrontabDiff:
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    unchanged: List[str] = field(default_factory=list)
    invalid_in_old: List[str] = field(default_factory=list)
    invalid_in_new: List[str] = field(default_factory=list)


def _parse_lines(text: str) -> List[str]:
    """Return non-blank, non-comment lines stripped of whitespace."""
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            lines.append(stripped)
    return lines


def diff(old_text: str, new_text: str) -> CrontabDiff:
    """Compare two crontab file contents and return a CrontabDiff."""
    old_lines = _parse_lines(old_text)
    new_lines = _parse_lines(new_text)

    old_set = set(old_lines)
    new_set = set(new_lines)

    result = CrontabDiff()

    for expr in old_set - new_set:
        if not is_valid(expr):
            result.invalid_in_old.append(expr)
        else:
            result.removed.append(expr)

    for expr in new_set - old_set:
        if not is_valid(expr):
            result.invalid_in_new.append(expr)
        else:
            result.added.append(expr)

    for expr in old_set & new_set:
        result.unchanged.append(expr)

    result.added.sort()
    result.removed.sort()
    result.unchanged.sort()
    result.invalid_in_old.sort()
    result.invalid_in_new.sort()

    return result

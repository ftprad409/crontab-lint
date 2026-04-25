"""Rename (replace) cron expressions across a crontab, returning a structured result."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from crontab_lint.parser import is_valid


@dataclass
class RenameResult:
    """Result of a bulk rename operation on a crontab."""

    lines: List[str]
    replacements: List[Tuple[int, str, str]]  # (line_number, old_expr, new_expr)
    skipped_invalid_source: List[str]
    skipped_invalid_target: List[str]


def total_replaced(result: RenameResult) -> int:
    """Return the number of lines that were actually replaced."""
    return len(result.replacements)


def _is_comment(line: str) -> bool:
    return line.strip().startswith("#")


def _is_blank(line: str) -> bool:
    return line.strip() == ""


def rename(
    lines: List[str],
    old_expr: str,
    new_expr: str,
) -> RenameResult:
    """Replace every occurrence of *old_expr* with *new_expr* in *lines*.

    Both expressions must be syntactically valid cron expressions; if either is
    invalid the function returns an unchanged copy of *lines* and records the
    problem in the appropriate ``skipped_invalid_*`` list.
    """
    skipped_invalid_source: List[str] = []
    skipped_invalid_target: List[str] = []

    if not is_valid(old_expr):
        skipped_invalid_source.append(old_expr)
        return RenameResult(
            lines=list(lines),
            replacements=[],
            skipped_invalid_source=skipped_invalid_source,
            skipped_invalid_target=[],
        )

    if not is_valid(new_expr):
        skipped_invalid_target.append(new_expr)
        return RenameResult(
            lines=list(lines),
            replacements=[],
            skipped_invalid_source=[],
            skipped_invalid_target=skipped_invalid_target,
        )

    result_lines: List[str] = []
    replacements: List[Tuple[int, str, str]] = []

    for lineno, raw in enumerate(lines, start=1):
        if _is_comment(raw) or _is_blank(raw):
            result_lines.append(raw)
            continue

        # Match on the expression portion (first five whitespace-separated tokens)
        parts = raw.split(None, 5)
        if len(parts) >= 5:
            candidate = " ".join(parts[:5])
            if candidate == old_expr:
                command = parts[5] if len(parts) == 6 else ""
                new_line = (new_expr + " " + command).rstrip() if command else new_expr
                result_lines.append(new_line)
                replacements.append((lineno, old_expr, new_expr))
                continue

        result_lines.append(raw)

    return RenameResult(
        lines=result_lines,
        replacements=replacements,
        skipped_invalid_source=[],
        skipped_invalid_target=[],
    )

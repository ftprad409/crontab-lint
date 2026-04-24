"""Merge multiple crontab files into a single deduplicated, sorted output."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Sequence

from crontab_lint.normalizer import normalize
from crontab_lint.parser import is_valid


@dataclass
class MergeResult:
    """Result of merging multiple crontab sources."""

    sources: List[str]
    lines: List[str]
    duplicate_count: int
    invalid_count: int
    comment_count: int


def _is_comment(line: str) -> bool:
    return line.strip().startswith("#")


def _is_blank(line: str) -> bool:
    return line.strip() == ""


def _read_source(source: str) -> List[str]:
    """Read lines from a file path or a raw multi-line string."""
    path = Path(source)
    if path.exists():
        return path.read_text().splitlines()
    return source.splitlines()


def merge(
    sources: Sequence[str],
    *,
    skip_invalid: bool = False,
    normalize_expressions: bool = True,
) -> MergeResult:
    """Merge crontab sources, deduplicating expressions.

    Args:
        sources: File paths or raw crontab strings to merge.
        skip_invalid: If True, invalid expressions are excluded from output.
        normalize_expressions: If True, normalise expressions before dedup.

    Returns:
        A MergeResult with the merged lines and statistics.
    """
    seen: set[str] = set()
    merged: List[str] = []
    duplicate_count = 0
    invalid_count = 0
    comment_count = 0

    for source in sources:
        for raw_line in _read_source(source):
            line = raw_line.rstrip()

            if _is_blank(line):
                continue

            if _is_comment(line):
                comment_count += 1
                merged.append(line)
                continue

            normalised = normalize(line) if normalize_expressions else line

            if not is_valid(normalised):
                invalid_count += 1
                if skip_invalid:
                    continue
                merged.append(line)
                continue

            key = normalised.strip()
            if key in seen:
                duplicate_count += 1
                continue

            seen.add(key)
            merged.append(normalised if normalize_expressions else line)

    return MergeResult(
        sources=list(sources),
        lines=merged,
        duplicate_count=duplicate_count,
        invalid_count=invalid_count,
        comment_count=comment_count,
    )

"""Deduplicator module for crontab-lint.

Detects duplicate or semantically equivalent crontab expressions
within a crontab file, helping users clean up redundant entries.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional

from .parser import is_valid, parse
from .normalizer import normalize


@dataclass
class DuplicateGroup:
    """Represents a group of duplicate or equivalent crontab expressions."""

    canonical: str
    """The normalized canonical form shared by all entries in the group."""

    entries: List[Tuple[int, str]]
    """List of (line_number, raw_expression) tuples that are duplicates."""

    @property
    def is_exact(self) -> bool:
        """True if all entries are byte-for-byte identical (before normalization)."""
        raw_values = [expr for _, expr in self.entries]
        return len(set(raw_values)) == 1


@dataclass
class DeduplicationResult:
    """Result of running deduplication over a list of crontab lines."""

    groups: List[DuplicateGroup] = field(default_factory=list)
    """Groups of duplicate expressions (only groups with 2+ entries)."""

    skipped: List[Tuple[int, str]] = field(default_factory=list)
    """Lines skipped because they are comments, blank, or invalid."""

    @property
    def has_duplicates(self) -> bool:
        return len(self.groups) > 0

    @property
    def duplicate_count(self) -> int:
        """Total number of redundant lines (each group contributes len-1 duplicates)."""
        return sum(len(g.entries) - 1 for g in self.groups)


def _is_comment(line: str) -> bool:
    return line.strip().startswith("#")


def _is_blank(line: str) -> bool:
    return line.strip() == ""


def _canonical_key(expression: str) -> Optional[str]:
    """Return a normalized canonical key for an expression, or None if invalid."""
    try:
        normalized = normalize(expression)
        parsed = parse(normalized)
        if parsed is None:
            return None
        # Build a stable key from the five fields after parsing
        return " ".join([
            parsed.minute,
            parsed.hour,
            parsed.day_of_month,
            parsed.month,
            parsed.day_of_week,
        ])
    except Exception:
        return None


def deduplicate(lines: List[str]) -> DeduplicationResult:
    """Analyse a list of crontab lines and identify duplicate expressions.

    Two expressions are considered duplicates when they share the same
    canonical (normalized + parsed) representation.

    Args:
        lines: Raw lines from a crontab file (may include comments/blanks).

    Returns:
        A :class:`DeduplicationResult` describing all duplicate groups and
        any lines that were skipped during analysis.
    """
    result = DeduplicationResult()

    # Map canonical_key -> list of (line_number, raw_expression)
    seen: dict = {}

    for lineno, raw in enumerate(lines, start=1):
        stripped = raw.strip()

        if _is_comment(stripped) or _is_blank(stripped):
            result.skipped.append((lineno, raw))
            continue

        if not is_valid(stripped):
            result.skipped.append((lineno, raw))
            continue

        key = _canonical_key(stripped)
        if key is None:
            result.skipped.append((lineno, raw))
            continue

        if key not in seen:
            seen[key] = []
        seen[key].append((lineno, stripped))

    # Build duplicate groups (only where more than one entry shares a key)
    for canonical_key, entries in seen.items():
        if len(entries) > 1:
            result.groups.append(
                DuplicateGroup(canonical=canonical_key, entries=entries)
            )

    return result

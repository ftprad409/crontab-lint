"""Tests for the deduplicator module."""

import pytest
from crontab_lint.deduplicator import (
    DuplicateGroup,
    DeduplicationResult,
    is_exact,
    has_duplicates,
    duplicate_count,
    deduplicate,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _result(lines):
    """Run deduplicate() on a list of raw crontab lines."""
    return deduplicate(lines)


# ---------------------------------------------------------------------------
# is_exact
# ---------------------------------------------------------------------------

def test_is_exact_identical_expressions():
    assert is_exact("* * * * * /bin/foo", "* * * * * /bin/foo") is True


def test_is_exact_different_expressions():
    assert is_exact("0 * * * * /bin/foo", "* * * * * /bin/foo") is False


def test_is_exact_ignores_leading_trailing_whitespace():
    assert is_exact("  * * * * * /bin/foo  ", "* * * * * /bin/foo") is True


# ---------------------------------------------------------------------------
# deduplicate — basic structure
# ---------------------------------------------------------------------------

def test_deduplicate_returns_deduplication_result():
    result = _result(["* * * * * /bin/foo"])
    assert isinstance(result, DeduplicationResult)


def test_deduplicate_no_duplicates_empty_groups():
    result = _result([
        "* * * * * /bin/foo",
        "0 6 * * * /bin/bar",
    ])
    assert len(result.groups) == 0


def test_deduplicate_skips_comments():
    result = _result([
        "# this is a comment",
        "* * * * * /bin/foo",
        "* * * * * /bin/foo",
    ])
    assert len(result.groups) == 1


def test_deduplicate_skips_blank_lines():
    result = _result([
        "",
        "   ",
        "* * * * * /bin/foo",
        "* * * * * /bin/foo",
    ])
    assert len(result.groups) == 1


# ---------------------------------------------------------------------------
# has_duplicates / duplicate_count
# ---------------------------------------------------------------------------

def test_has_duplicates_true_when_duplicates_present():
    result = _result([
        "* * * * * /bin/foo",
        "* * * * * /bin/foo",
    ])
    assert has_duplicates(result) is True


def test_has_duplicates_false_when_no_duplicates():
    result = _result(["* * * * * /bin/foo", "0 6 * * * /bin/bar"])
    assert has_duplicates(result) is False


def test_duplicate_count_zero_when_clean():
    result = _result(["* * * * * /bin/foo", "0 6 * * * /bin/bar"])
    assert duplicate_count(result) == 0


def test_duplicate_count_reflects_extra_occurrences():
    # Three identical lines → 2 duplicates (the 2nd and 3rd occurrences)
    result = _result([
        "* * * * * /bin/foo",
        "* * * * * /bin/foo",
        "* * * * * /bin/foo",
    ])
    assert duplicate_count(result) == 2


# ---------------------------------------------------------------------------
# DuplicateGroup contents
# ---------------------------------------------------------------------------

def test_duplicate_group_canonical_expression():
    result = _result([
        "0 12 * * * /usr/bin/backup",
        "0 12 * * * /usr/bin/backup",
    ])
    group = result.groups[0]
    assert group.canonical == "0 12 * * * /usr/bin/backup"


def test_duplicate_group_line_numbers_recorded():
    result = _result([
        "# comment",
        "0 12 * * * /usr/bin/backup",
        "0 12 * * * /usr/bin/backup",
    ])
    group = result.groups[0]
    # Lines 2 and 3 (1-indexed), comment on line 1 is skipped
    assert 2 in group.line_numbers
    assert 3 in group.line_numbers


def test_duplicate_group_occurrences_count():
    result = _result([
        "*/5 * * * * /bin/check",
        "*/5 * * * * /bin/check",
        "*/5 * * * * /bin/check",
    ])
    group = result.groups[0]
    assert group.occurrences == 3


# ---------------------------------------------------------------------------
# Multiple distinct duplicate groups
# ---------------------------------------------------------------------------

def test_multiple_duplicate_groups_detected():
    result = _result([
        "* * * * * /bin/a",
        "* * * * * /bin/a",
        "0 6 * * * /bin/b",
        "0 6 * * * /bin/b",
    ])
    assert len(result.groups) == 2


def test_unique_lines_preserved_in_result():
    lines = [
        "* * * * * /bin/foo",
        "* * * * * /bin/foo",
        "0 6 * * * /bin/bar",
    ]
    result = _result(lines)
    assert "0 6 * * * /bin/bar" in result.unique_lines
    assert result.unique_lines.count("* * * * * /bin/foo") == 1

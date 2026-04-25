"""Tests for crontab_lint.renamer and crontab_lint.formatter_renamer."""

from __future__ import annotations

import pytest

from crontab_lint.renamer import rename, total_replaced, RenameResult
from crontab_lint.formatter_renamer import format_rename_result, format_rename_diff


OLD = "0 9 * * 1"
NEW = "30 9 * * 1"


# ---------------------------------------------------------------------------
# rename()
# ---------------------------------------------------------------------------

def test_rename_returns_rename_result():
    result = rename([OLD + " /usr/bin/backup"], OLD, NEW)
    assert isinstance(result, RenameResult)


def test_rename_replaces_matching_expression():
    lines = [OLD + " /usr/bin/backup"]
    result = rename(lines, OLD, NEW)
    assert result.lines[0].startswith(NEW)


def test_rename_records_replacement_tuple():
    lines = [OLD + " /usr/bin/backup"]
    result = rename(lines, OLD, NEW)
    assert len(result.replacements) == 1
    lineno, old, new = result.replacements[0]
    assert lineno == 1
    assert old == OLD
    assert new == NEW


def test_rename_preserves_command():
    cmd = "/usr/bin/backup --verbose"
    lines = [f"{OLD} {cmd}"]
    result = rename(lines, OLD, NEW)
    assert cmd in result.lines[0]


def test_rename_skips_comments():
    lines = [f"# {OLD} some comment", f"{OLD} /bin/true"]
    result = rename(lines, OLD, NEW)
    assert result.lines[0] == f"# {OLD} some comment"
    assert result.lines[1].startswith(NEW)


def test_rename_skips_blank_lines():
    lines = ["", f"{OLD} /bin/true"]
    result = rename(lines, OLD, NEW)
    assert result.lines[0] == ""


def test_rename_multiple_occurrences():
    lines = [f"{OLD} /bin/a", f"{OLD} /bin/b"]
    result = rename(lines, OLD, NEW)
    assert total_replaced(result) == 2


def test_rename_invalid_source_skipped():
    result = rename(["not a cron"], "not a cron", NEW)
    assert result.skipped_invalid_source == ["not a cron"]
    assert total_replaced(result) == 0


def test_rename_invalid_target_skipped():
    result = rename([f"{OLD} /bin/true"], OLD, "bad expression")
    assert result.skipped_invalid_target == ["bad expression"]
    assert total_replaced(result) == 0


def test_rename_no_match_leaves_lines_unchanged():
    lines = ["0 8 * * * /bin/true"]
    result = rename(lines, OLD, NEW)
    assert result.lines == lines
    assert total_replaced(result) == 0


# ---------------------------------------------------------------------------
# format_rename_result()
# ---------------------------------------------------------------------------

def test_format_rename_result_contains_header():
    result = rename([f"{OLD} /bin/true"], OLD, NEW)
    output = format_rename_result(result)
    assert "Rename Report" in output


def test_format_rename_result_shows_count():
    result = rename([f"{OLD} /bin/true"], OLD, NEW)
    output = format_rename_result(result)
    assert "1" in output


def test_format_rename_result_invalid_source_error():
    result = rename(["x"], "x y z", NEW)
    output = format_rename_result(result)
    assert "ERROR" in output


def test_format_rename_diff_no_changes():
    result = rename(["0 8 * * * /bin/true"], OLD, NEW)
    output = format_rename_diff(result)
    assert "no changes" in output


def test_format_rename_diff_shows_old_and_new():
    result = rename([f"{OLD} /bin/true"], OLD, NEW)
    output = format_rename_diff(result)
    assert "-" in output
    assert "+" in output

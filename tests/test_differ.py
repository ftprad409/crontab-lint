"""Tests for crontab_lint.differ and crontab_lint.formatter_diff."""

import pytest
from crontab_lint.differ import diff, _parse_lines, CrontabDiff
from crontab_lint.formatter_diff import format_diff


OLD_CRONTAB = """
# daily backup
0 2 * * * /usr/bin/backup
*/5 * * * * /usr/bin/monitor
0 12 * * 1 /usr/bin/report
"""

NEW_CRONTAB = """
# daily backup updated
0 3 * * * /usr/bin/backup
*/5 * * * * /usr/bin/monitor
0 0 * * * /usr/bin/cleanup
"""


def test_parse_lines_skips_comments_and_blanks():
    text = "# comment\n\n0 * * * * cmd\n"
    assert _parse_lines(text) == ["0 * * * * cmd"]


def test_parse_lines_strips_whitespace():
    text = "  0 * * * * cmd  \n"
    assert _parse_lines(text) == ["0 * * * * cmd"]


def test_diff_detects_added():
    result = diff(OLD_CRONTAB, NEW_CRONTAB)
    assert "0 0 * * * /usr/bin/cleanup" in result.added


def test_diff_detects_removed():
    result = diff(OLD_CRONTAB, NEW_CRONTAB)
    assert "0 12 * * 1 /usr/bin/report" in result.removed


def test_diff_detects_unchanged():
    result = diff(OLD_CRONTAB, NEW_CRONTAB)
    assert "*/5 * * * * /usr/bin/monitor" in result.unchanged


def test_diff_invalid_expressions_separated():
    old = "0 * * * * valid_cmd\nbad expression here\n"
    new = "0 * * * * valid_cmd\nanother bad one\n"
    result = diff(old, new)
    assert "bad expression here" in result.invalid_in_old
    assert "another bad one" in result.invalid_in_new


def test_diff_no_changes():
    result = diff(OLD_CRONTAB, OLD_CRONTAB)
    assert result.added == []
    assert result.removed == []
    assert len(result.unchanged) > 0


def test_format_diff_contains_header():
    result = diff(OLD_CRONTAB, NEW_CRONTAB)
    output = format_diff(result)
    assert "Crontab Diff Report" in output


def test_format_diff_shows_added():
    result = diff(OLD_CRONTAB, NEW_CRONTAB)
    output = format_diff(result)
    assert "+ 0 0 * * * /usr/bin/cleanup" in output


def test_format_diff_shows_removed():
    result = diff(OLD_CRONTAB, NEW_CRONTAB)
    output = format_diff(result)
    assert "- 0 12 * * 1 /usr/bin/report" in output


def test_format_diff_total_changes():
    result = diff(OLD_CRONTAB, NEW_CRONTAB)
    output = format_diff(result)
    assert "Total changes:" in output


def test_format_diff_no_changes_message():
    result = diff(OLD_CRONTAB, OLD_CRONTAB)
    output = format_diff(result)
    assert "Added: none" in output
    assert "Removed: none" in output

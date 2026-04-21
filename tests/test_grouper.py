"""Tests for crontab_lint.grouper and crontab_lint.formatter_grouper."""

import pytest
from crontab_lint.grouper import _classify, group, CrontabGroup
from crontab_lint.formatter_grouper import format_group, format_group_report


def test_classify_every_minute():
    assert _classify("* * * * *") == "every_minute"


def test_classify_every_hour():
    assert _classify("30 * * * *") == "every_hour"


def test_classify_daily():
    assert _classify("0 9 * * *") == "daily"


def test_classify_weekly():
    assert _classify("0 9 * * 1") == "weekly"


def test_classify_monthly():
    assert _classify("0 9 1 * *") == "monthly"


def test_classify_yearly():
    assert _classify("0 9 1 1 *") == "yearly"


def test_group_separates_by_frequency():
    exprs = ["* * * * *", "0 9 * * *", "0 9 1 * *"]
    result = group(exprs)
    assert "every_minute" in result
    assert "daily" in result
    assert "monthly" in result


def test_group_skips_comments_and_blanks():
    exprs = ["# comment", "", "* * * * *"]
    result = group(exprs)
    assert "every_minute" in result
    assert len(result["every_minute"].expressions) == 1


def test_group_invalid_expressions():
    exprs = ["not a cron", "99 * * * *"]
    result = group(exprs)
    assert "invalid" in result
    assert len(result["invalid"].expressions) == 2


def test_group_multiple_same_label():
    exprs = ["0 9 * * *", "0 12 * * *", "0 18 * * *"]
    result = group(exprs)
    assert len(result["daily"].expressions) == 3


def test_format_group_contains_label():
    grp = CrontabGroup(label="daily", expressions=["0 9 * * *"])
    output = format_group(grp)
    assert "Daily" in output
    assert "0 9 * * *" in output


def test_format_group_shows_count():
    grp = CrontabGroup(label="weekly", expressions=["0 9 * * 1", "0 9 * * 5"])
    output = format_group(grp)
    assert "2 expression(s)" in output


def test_format_group_report_has_header():
    exprs = ["* * * * *", "0 9 * * *"]
    groups = group(exprs)
    report = format_group_report(groups)
    assert "=== Crontab Groups ===" in report


def test_format_group_report_empty():
    report = format_group_report({})
    assert "No expressions" in report


def test_format_group_report_order():
    exprs = ["0 9 1 * *", "* * * * *", "0 9 * * *"]
    groups = group(exprs)
    report = format_group_report(groups)
    every_min_pos = report.index("Every Minute")
    daily_pos = report.index("Daily")
    monthly_pos = report.index("Monthly")
    assert every_min_pos < daily_pos < monthly_pos

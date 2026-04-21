"""Tests for crontab_lint.formatter_schedule."""

from datetime import datetime
from crontab_lint.formatter_schedule import format_next_run, format_schedule_report


def test_format_next_run_valid():
    dt = datetime(2024, 6, 1, 9, 30)
    line = format_next_run("0 9 * * *", dt)
    assert "2024-06-01 09:30" in line
    assert "0 9 * * *" in line


def test_format_next_run_invalid():
    line = format_next_run("bad expr", None)
    assert "invalid expression" in line
    assert "bad expr" in line


def test_format_next_run_returns_string():
    """Ensure format_next_run always returns a string regardless of input."""
    assert isinstance(format_next_run("0 9 * * *", datetime(2024, 1, 1, 9, 0)), str)
    assert isinstance(format_next_run("bad", None), str)


def test_format_schedule_report_header():
    results = [("* * * * *", datetime(2024, 1, 1, 0, 1))]
    report = format_schedule_report(results)
    assert "Next Scheduled Runs" in report


def test_format_schedule_report_contains_all_entries():
    results = [
        ("0 9 * * *", datetime(2024, 6, 1, 9, 0)),
        ("bad", None),
    ]
    report = format_schedule_report(results)
    assert "0 9 * * *" in report
    assert "bad" in report
    assert "invalid expression" in report


def test_format_schedule_report_separators():
    report = format_schedule_report([])
    assert report.count("=" * 60) >= 2


def test_format_schedule_report_empty_returns_string():
    """Ensure format_schedule_report returns a string even for empty input."""
    report = format_schedule_report([])
    assert isinstance(report, str)

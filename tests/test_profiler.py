"""Tests for crontab_lint.profiler and crontab_lint.formatter_profiler."""

import pytest
from crontab_lint.profiler import profile, CrontabProfile
from crontab_lint.formatter_profiler import (
    format_hourly_chart,
    format_minutely_chart,
    format_profile_report,
)


LINES = [
    "# daily backup",
    "0 2 * * * /backup.sh",
    "30 2 * * * /cleanup.sh",
    "*/5 * * * * /heartbeat.sh",
    "",
    "not a valid expression",
]


def test_profile_returns_crontab_profile():
    result = profile(LINES)
    assert isinstance(result, CrontabProfile)


def test_profile_counts_valid_expressions():
    result = profile(LINES)
    assert result.total_expressions == 3


def test_profile_counts_skipped_expressions():
    result = profile(LINES)
    assert result.skipped_expressions == 1


def test_profile_hourly_load_keys():
    result = profile(LINES)
    assert set(result.hourly_load.keys()) == set(range(24))


def test_profile_minutely_load_keys():
    result = profile(LINES)
    assert set(result.minutely_load.keys()) == set(range(60))


def test_profile_busiest_hour_is_int():
    result = profile(LINES)
    assert isinstance(result.busiest_hour, int)
    assert 0 <= result.busiest_hour <= 23


def test_profile_busiest_minute_is_int():
    result = profile(LINES)
    assert isinstance(result.busiest_minute, int)
    assert 0 <= result.busiest_minute <= 59


def test_profile_wildcard_hour_increments_all_hours():
    result = profile(["*/5 * * * * /heartbeat.sh"])
    for h in range(24):
        assert result.hourly_load[h] == 1


def test_profile_empty_lines():
    result = profile([])
    assert result.total_expressions == 0
    assert result.skipped_expressions == 0


def test_format_hourly_chart_contains_hours():
    result = profile(LINES)
    chart = format_hourly_chart(result)
    assert "02:00" in chart
    assert "busiest" in chart


def test_format_minutely_chart_contains_minutes():
    result = profile(LINES)
    chart = format_minutely_chart(result)
    assert "Top 5 busiest minutes" in chart


def test_format_profile_report_contains_sections():
    result = profile(LINES)
    report = format_profile_report(result)
    assert "Crontab Load Profile" in report
    assert "Expressions analysed" in report
    assert "Busiest hour" in report
    assert "Busiest minute" in report


def test_format_profile_report_is_string():
    result = profile(LINES)
    assert isinstance(format_profile_report(result), str)

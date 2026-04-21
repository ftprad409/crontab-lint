"""Tests for crontab_lint.normalizer."""

import pytest
from crontab_lint.normalizer import normalize


def test_normalize_at_yearly():
    assert normalize("@yearly") == "0 0 1 1 *"


def test_normalize_at_annually():
    assert normalize("@annually") == "0 0 1 1 *"


def test_normalize_at_monthly():
    assert normalize("@monthly") == "0 0 1 * *"


def test_normalize_at_weekly():
    assert normalize("@weekly") == "0 0 * * 0"


def test_normalize_at_daily():
    assert normalize("@daily") == "0 0 * * *"


def test_normalize_at_midnight():
    assert normalize("@midnight") == "0 0 * * *"


def test_normalize_at_hourly():
    assert normalize("@hourly") == "0 * * * *"


def test_normalize_alias_case_insensitive():
    assert normalize("@Daily") == "0 0 * * *"
    assert normalize("@HOURLY") == "0 * * * *"


def test_normalize_named_month():
    result = normalize("0 0 1 Jan *")
    assert result == "0 0 1 1 *"


def test_normalize_named_month_case_insensitive():
    result = normalize("0 0 1 DEC *")
    assert result == "0 0 1 12 *"


def test_normalize_named_weekday():
    result = normalize("0 9 * * Mon")
    assert result == "0 9 * * 1"


def test_normalize_named_weekday_sunday():
    result = normalize("0 0 * * Sun")
    assert result == "0 0 * * 0"


def test_normalize_named_weekday_saturday():
    result = normalize("30 18 * * Sat")
    assert result == "30 18 * * 6"


def test_normalize_plain_expression_unchanged():
    expr = "5 4 * * *"
    assert normalize(expr) == expr


def test_normalize_strips_extra_whitespace():
    result = normalize("  0 0 1 1 *  ")
    assert result == "0 0 1 1 *"


def test_normalize_comment_returns_none():
    assert normalize("# this is a comment") is None


def test_normalize_blank_line_returns_none():
    assert normalize("") is None
    assert normalize("   ") is None


def test_normalize_invalid_field_count_returns_as_is():
    # Too few fields — return as-is so parser can report the error
    result = normalize("* * *")
    assert result == "* * *"

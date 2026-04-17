"""Tests for crontab parser and explainer."""

import pytest
from crontab_lint.parser import parse
from crontab_lint.explainer import explain


@pytest.mark.parametrize("expression", [
    "* * * * *",
    "0 12 * * 1",
    "*/15 6-18 1,15 * 1-5",
    "30 8 1 1 0",
])
def test_valid_expressions(expression):
    result = parse(expression)
    assert result.is_valid, f"Expected valid, got errors: {result.errors}"


@pytest.mark.parametrize("expression,expected_error_fragment", [
    ("60 * * * *", "minute"),
    ("* 25 * * *", "hour"),
    ("* * 32 * *", "day_of_month"),
    ("* * * 13 *", "month"),
    ("* * * * 8", "day_of_week"),
    ("* * *", "Expected 5 fields"),
    ("abc * * * *", "minute"),
])
def test_invalid_expressions(expression, expected_error_fragment):
    result = parse(expression)
    assert not result.is_valid
    assert any(expected_error_fragment in e for e in result.errors)


def test_explain_wildcard():
    expr = parse("* * * * *")
    explanation = explain(expr)
    assert "every minute" in explanation
    assert "every hour" in explanation


def test_explain_specific():
    expr = parse("0 12 * * 1")
    explanation = explain(expr)
    assert "12" in explanation
    assert "Mon" in explanation


def test_explain_invalid():
    expr = parse("99 * * * *")
    explanation = explain(expr)
    assert explanation.startswith("Invalid expression")


def test_explain_step():
    expr = parse("*/15 * * * *")
    explanation = explain(expr)
    assert "every 15 minute(s)" in explanation


def test_explain_month_names():
    expr = parse("0 0 1 6 *")
    explanation = explain(expr)
    assert "Jun" in explanation

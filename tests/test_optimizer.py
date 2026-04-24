"""Tests for crontab_lint.optimizer and crontab_lint.formatter_optimizer."""

import pytest
from crontab_lint.optimizer import optimize, OptimizationResult, OptimizationSuggestion
from crontab_lint.formatter_optimizer import format_optimization_result, format_optimization_report


# --- optimizer unit tests ---

def test_optimize_returns_result_instance():
    result = optimize("* * * * *")
    assert isinstance(result, OptimizationResult)


def test_optimize_invalid_expression_no_suggestions():
    result = optimize("invalid expression")
    assert not result.has_suggestions


def test_optimize_wildcard_suggests_at_reboot():
    result = optimize("* * * * *")
    assert result.has_suggestions
    assert any(s.suggested == "@reboot" for s in result.suggestions)


def test_optimize_daily_suggests_shorthand():
    result = optimize("0 0 * * *")
    assert result.has_suggestions
    assert any(s.suggested == "@daily" for s in result.suggestions)


def test_optimize_hourly_suggests_shorthand():
    result = optimize("0 * * * *")
    assert any(s.suggested == "@hourly" for s in result.suggestions)


def test_optimize_yearly_suggests_shorthand():
    result = optimize("0 0 1 1 *")
    assert any(s.suggested == "@yearly" for s in result.suggestions)


def test_optimize_step_one_minute_suggests_wildcard():
    result = optimize("*/1 * * * *")
    assert any(s.suggested == "*" and "minute" in s.reason for s in result.suggestions)


def test_optimize_step_one_hour_suggests_wildcard():
    result = optimize("* */1 * * *")
    assert any(s.suggested == "*" and "hour" in s.reason for s in result.suggestions)


def test_optimize_no_suggestion_for_valid_complex():
    result = optimize("15 4 * * 1-5")
    assert not result.has_suggestions


def test_has_suggestions_property_false_when_empty():
    result = OptimizationResult(expression="15 4 * * 1-5")
    assert not result.has_suggestions


def test_has_suggestions_property_true_when_filled():
    result = OptimizationResult(
        expression="* * * * *",
        suggestions=[OptimizationSuggestion("* * * * *", "@reboot", "reason")],
    )
    assert result.has_suggestions


# --- formatter tests ---

def test_format_no_suggestions_contains_checkmark():
    result = optimize("15 4 * * 1-5")
    output = format_optimization_result(result)
    assert "✔" in output


def test_format_with_suggestion_contains_arrow():
    result = optimize("0 0 * * *")
    output = format_optimization_result(result)
    assert "➤" in output


def test_format_report_contains_header():
    results = [optimize("0 0 * * *"), optimize("15 4 * * 1-5")]
    report = format_optimization_report(results)
    assert "Optimization Report" in report


def test_format_report_contains_totals():
    results = [optimize("0 0 * * *"), optimize("15 4 * * 1-5")]
    report = format_optimization_report(results)
    assert "Total expressions" in report
    assert "2" in report


def test_format_report_empty_list():
    report = format_optimization_report([])
    assert "No expressions" in report

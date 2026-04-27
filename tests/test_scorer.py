"""Tests for crontab_lint.scorer and crontab_lint.formatter_scorer."""
import pytest
from crontab_lint.scorer import score, _score_expression, _grade, ScorerResult
from crontab_lint.formatter_scorer import format_score_entry, format_score_report


def test_score_returns_scorer_result():
    result = score(["* * * * * /bin/true"])
    assert isinstance(result, ScorerResult)


def test_score_skips_comments_and_blanks():
    result = score(["# comment", "", "  ", "0 * * * * /bin/true"])
    assert len(result.scores) == 1


def test_score_invalid_expression_grade_f():
    entry = _score_expression("not a cron")
    assert entry.grade == "F"
    assert not entry.valid


def test_score_every_minute_high_score():
    entry = _score_expression("* * * * * /bin/true")
    assert entry.valid
    assert entry.score >= 5  # wildcards + heavy penalty


def test_score_specific_expression_low_score():
    entry = _score_expression("30 2 * * 0 /bin/backup")
    assert entry.valid
    assert entry.score <= 4


def test_grade_boundaries():
    assert _grade(0) == "A"
    assert _grade(2) == "A"
    assert _grade(3) == "B"
    assert _grade(5) == "B"
    assert _grade(6) == "C"
    assert _grade(8) == "C"
    assert _grade(9) == "D"


def test_average_score_empty():
    result = score([])
    assert result.average_score == 0.0


def test_average_score_computed():
    result = score(["0 0 * * * cmd", "* * * * * cmd"])
    assert result.average_score > 0


def test_highest_risk_returns_max():
    result = score(["0 0 * * * cmd", "* * * * * cmd"])
    assert result.highest_risk is not None
    assert result.highest_risk.expression == "* * * * * cmd"


def test_highest_risk_none_when_empty():
    result = score([])
    assert result.highest_risk is None


def test_reasons_populated_for_wildcards():
    entry = _score_expression("* 0 * * * cmd")
    assert any("minute" in r for r in entry.reasons)


def test_step_value_noted_in_reasons():
    entry = _score_expression("*/15 * * * * cmd")
    assert any("Step" in r or "step" in r for r in entry.reasons)


def test_format_score_entry_invalid_shows_invalid():
    entry = _score_expression("bad cron")
    output = format_score_entry(entry)
    assert "invalid" in output.lower()


def test_format_score_entry_valid_shows_score():
    entry = _score_expression("0 12 * * * cmd")
    output = format_score_entry(entry)
    assert "score" in output


def test_format_score_report_header():
    result = score(["0 0 * * * cmd"])
    report = format_score_report(result)
    assert "Score Report" in report


def test_format_score_report_empty():
    result = score([])
    report = format_score_report(result)
    assert "No expressions" in report


def test_format_score_report_contains_average():
    result = score(["0 0 * * * cmd", "*/5 * * * * cmd"])
    report = format_score_report(result)
    assert "Average" in report

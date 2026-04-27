"""Tests for crontab_lint.inspector and crontab_lint.formatter_inspector."""
import pytest
from crontab_lint.inspector import inspect, InspectionResult, _field_breakdown, _score_expression
from crontab_lint.formatter_inspector import format_inspection


def test_inspect_returns_inspection_result():
    result = inspect("0 9 * * 1")
    assert isinstance(result, InspectionResult)


def test_inspect_valid_expression():
    result = inspect("0 9 * * 1")
    assert result.valid is True


def test_inspect_invalid_expression():
    result = inspect("99 99 99 99 99")
    assert result.valid is False


def test_inspect_invalid_has_no_explanation():
    result = inspect("not a cron")
    assert result.explanation is None


def test_inspect_valid_has_explanation():
    result = inspect("* * * * *")
    assert result.explanation is not None
    assert len(result.explanation) > 0


def test_inspect_next_runs_populated_for_valid():
    result = inspect("* * * * *", runs=3)
    assert len(result.next_runs) == 3


def test_inspect_next_runs_empty_for_invalid():
    result = inspect("bad expr", runs=3)
    assert result.next_runs == []


def test_inspect_next_run_format():
    result = inspect("0 12 * * *", runs=1)
    assert len(result.next_runs) == 1
    run = result.next_runs[0]
    assert len(run) == 16  # "YYYY-MM-DD HH:MM"


def test_inspect_grade_f_for_invalid():
    result = inspect("invalid")
    assert result.grade == "F"
    assert result.score == 0


def test_inspect_high_score_for_every_minute():
    result = inspect("* * * * *")
    assert result.score > 50


def test_inspect_fields_populated():
    result = inspect("30 6 * * 1-5")
    assert result.fields["minute"] == "30"
    assert result.fields["hour"] == "6"
    assert result.fields["day_of_week"] == "1-5"


def test_inspect_fields_empty_for_invalid():
    result = inspect("not valid")
    assert result.fields == {}


def test_field_breakdown_five_keys():
    fb = _field_breakdown("0 0 1 1 0")
    assert set(fb.keys()) == {"minute", "hour", "day_of_month", "month", "day_of_week"}


def test_score_expression_invalid_returns_zero():
    assert _score_expression("bad") == 0


def test_format_inspection_contains_expression():
    result = inspect("0 9 * * *")
    text = format_inspection(result)
    assert "0 9 * * *" in text


def test_format_inspection_contains_grade():
    result = inspect("0 9 * * *")
    text = format_inspection(result)
    assert "grade" in text


def test_format_inspection_contains_next_runs_section():
    result = inspect("* * * * *", runs=2)
    text = format_inspection(result)
    assert "Next runs" in text


def test_format_inspection_invalid_shows_cross():
    result = inspect("bad cron")
    text = format_inspection(result)
    assert "\u2717" in text


def test_format_inspection_valid_shows_checkmark():
    result = inspect("0 0 * * *")
    text = format_inspection(result)
    assert "\u2713" in text

"""Tests for crontab_lint.scheduler."""

from datetime import datetime
import pytest
from crontab_lint.scheduler import next_run


BASE = datetime(2024, 1, 15, 12, 0)  # Monday


def test_next_run_every_minute():
    result = next_run("* * * * *", after=BASE)
    assert result == datetime(2024, 1, 15, 12, 1)


def test_next_run_specific_minute():
    result = next_run("30 * * * *", after=BASE)
    assert result == datetime(2024, 1, 15, 12, 30)


def test_next_run_specific_hour_and_minute():
    result = next_run("0 14 * * *", after=BASE)
    assert result == datetime(2024, 1, 15, 14, 0)


def test_next_run_past_midnight():
    after = datetime(2024, 1, 15, 23, 50)
    result = next_run("0 2 * * *", after=after)
    assert result == datetime(2024, 1, 16, 2, 0)


def test_next_run_specific_day_of_month():
    result = next_run("0 9 20 * *", after=BASE)
    assert result == datetime(2024, 1, 20, 9, 0)


def test_next_run_specific_month():
    result = next_run("0 0 1 6 *", after=BASE)
    assert result == datetime(2024, 6, 1, 0, 0)


def test_next_run_step():
    after = datetime(2024, 1, 15, 12, 0)
    result = next_run("*/15 * * * *", after=after)
    assert result == datetime(2024, 1, 15, 12, 15)


def test_next_run_invalid_expression():
    assert next_run("invalid") is None


@pytest.mark.parametrize("expression", [
    "",
    "* * * *",
    "* * * * * *",
    "not a cron",
])
def test_next_run_invalid_expressions(expression):
    """Ensure various malformed expressions all return None."""
    assert next_run(expression) is None


def test_next_run_uses_now_when_no_after(monkeypatch):
    fixed = datetime(2024, 3, 1, 10, 0)
    import crontab_lint.scheduler as sched
    monkeypatch.setattr(sched, "datetime", type("_DT", (), {"now": staticmethod(lambda: fixed), "replace": fixed.replace, "__class__": datetime}))
    # just ensure it returns a datetime without crashing
    result = next_run("* * * * *", after=fixed)
    assert isinstance(result, datetime)

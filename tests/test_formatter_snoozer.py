"""Tests for crontab_lint.formatter_snoozer."""
from __future__ import annotations

from datetime import datetime, timedelta

from crontab_lint.snoozer import SnoozedExpression, SnoozeResult, snooze
from crontab_lint.formatter_snoozer import (
    format_active_snoozes,
    format_snoozed_entry,
    format_snooze_result,
)

VALID = "0 9 * * 1"
ANOTHER = "30 18 * * *"


def _future() -> datetime:
    return datetime.utcnow() + timedelta(hours=2)


def test_format_snoozed_entry_contains_expression():
    entry = SnoozedExpression(VALID, _future())
    text = format_snoozed_entry(entry)
    assert VALID in text


def test_format_snoozed_entry_active_label():
    entry = SnoozedExpression(VALID, _future())
    assert "ACTIVE" in format_snoozed_entry(entry)


def test_format_snoozed_entry_expired_label():
    entry = SnoozedExpression(VALID, datetime.utcnow() - timedelta(seconds=1))
    assert "EXPIRED" in format_snoozed_entry(entry)


def test_format_snoozed_entry_shows_reason():
    entry = SnoozedExpression(VALID, _future(), reason="deploy")
    assert "deploy" in format_snoozed_entry(entry)


def test_format_snooze_result_header():
    result = snooze([VALID], duration_minutes=10)
    text = format_snooze_result(result)
    assert "Snooze Report" in text


def test_format_snooze_result_lists_snoozed():
    result = snooze([VALID, ANOTHER], duration_minutes=10)
    text = format_snooze_result(result)
    assert VALID in text
    assert ANOTHER in text


def test_format_snooze_result_no_new_message():
    result = SnoozeResult()
    text = format_snooze_result(result)
    assert "No new expressions snoozed" in text


def test_format_snooze_result_lists_invalid():
    result = snooze(["bad expr"], duration_minutes=5)
    text = format_snooze_result(result)
    assert "invalid" in text.lower()
    assert "bad expr" in text


def test_format_active_snoozes_empty():
    assert "No active snoozes" in format_active_snoozes([])


def test_format_active_snoozes_lists_active():
    entries = [SnoozedExpression(VALID, _future())]
    text = format_active_snoozes(entries)
    assert VALID in text
    assert "Active snoozes" in text

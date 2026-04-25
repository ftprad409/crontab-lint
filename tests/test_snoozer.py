"""Tests for crontab_lint.snoozer."""
from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from crontab_lint.snoozer import (
    SnoozedExpression,
    SnoozeResult,
    active_snoozes,
    lift_snooze,
    snooze,
)

VALID = "0 9 * * 1"
ANOTHER = "30 18 * * *"
INVALID = "not a cron"


def test_snooze_returns_snooze_result():
    result = snooze([VALID], duration_minutes=30)
    assert isinstance(result, SnoozeResult)


def test_snooze_valid_expression_is_snoozed():
    result = snooze([VALID], duration_minutes=15)
    assert result.total_snoozed == 1
    assert result.snoozed[0].expression == VALID


def test_snooze_invalid_expression_skipped():
    result = snooze([INVALID], duration_minutes=10)
    assert result.total_snoozed == 0
    assert INVALID in result.skipped_invalid


def test_snooze_already_active_skipped():
    existing = [SnoozedExpression(VALID, datetime.utcnow() + timedelta(hours=1))]
    result = snooze([VALID], duration_minutes=10, existing=existing)
    assert result.total_snoozed == 0
    assert VALID in result.skipped_already_snoozed


def test_snooze_expired_entry_re_snoozed():
    existing = [SnoozedExpression(VALID, datetime.utcnow() - timedelta(minutes=1))]
    result = snooze([VALID], duration_minutes=10, existing=existing)
    assert result.total_snoozed == 1


def test_snooze_reason_stored():
    result = snooze([VALID], duration_minutes=5, reason="maintenance")
    assert result.snoozed[0].reason == "maintenance"


def test_snooze_duration_zero_raises():
    with pytest.raises(ValueError):
        snooze([VALID], duration_minutes=0)


def test_snooze_comments_and_blanks_ignored():
    result = snooze(["# comment", "", VALID], duration_minutes=5)
    assert result.total_snoozed == 1


def test_snoozed_expression_is_active():
    entry = SnoozedExpression(VALID, datetime.utcnow() + timedelta(hours=1))
    assert entry.is_active is True


def test_snoozed_expression_expired():
    entry = SnoozedExpression(VALID, datetime.utcnow() - timedelta(seconds=1))
    assert entry.is_active is False


def test_active_snoozes_filters_expired():
    entries = [
        SnoozedExpression(VALID, datetime.utcnow() + timedelta(hours=1)),
        SnoozedExpression(ANOTHER, datetime.utcnow() - timedelta(hours=1)),
    ]
    active = active_snoozes(entries)
    assert len(active) == 1
    assert active[0].expression == VALID


def test_lift_snooze_removes_expression():
    entries = [
        SnoozedExpression(VALID, datetime.utcnow() + timedelta(hours=1)),
        SnoozedExpression(ANOTHER, datetime.utcnow() + timedelta(hours=1)),
    ]
    remaining = lift_snooze(VALID, entries)
    assert all(e.expression != VALID for e in remaining)
    assert len(remaining) == 1

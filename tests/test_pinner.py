"""Tests for crontab_lint.pinner and crontab_lint.formatter_pinner."""

from datetime import datetime

import pytest

from crontab_lint.pinner import PinnedExpression, PinResult, pin
from crontab_lint.formatter_pinner import (
    format_pinned_entry,
    format_pin_result,
    format_pinned_list,
)

_NOW = datetime(2024, 6, 15, 12, 0, 0)
_VALID = "0 9 * * 1"
_VALID2 = "30 18 * * 5"
_INVALID = "99 99 99 99 99"


def _pin(*exprs, reason="test", existing=None):
    return pin(list(exprs), reason=reason, pinned_by="tester", existing=existing, now=_NOW)


# --- pin() core logic ---

def test_pin_returns_pin_result():
    result = _pin(_VALID)
    assert isinstance(result, PinResult)


def test_pin_valid_expression_is_pinned():
    result = _pin(_VALID)
    assert result.total_pinned == 1
    assert result.pinned[0].expression == _VALID


def test_pin_invalid_expression_skipped():
    result = _pin(_INVALID)
    assert result.total_pinned == 0
    assert _INVALID in result.skipped_invalid


def test_pin_already_pinned_skipped():
    existing = [PinnedExpression(_VALID, "prev", _NOW, "tester")]
    result = _pin(_VALID, existing=existing)
    assert result.total_pinned == 0
    assert _VALID in result.skipped_already_pinned


def test_pin_skips_comments_and_blanks():
    result = _pin("# comment", "", "   ")
    assert result.total_pinned == 0
    assert result.total_skipped == 0


def test_pin_multiple_mixed():
    result = _pin(_VALID, _VALID2, _INVALID)
    assert result.total_pinned == 2
    assert len(result.skipped_invalid) == 1


def test_pin_stores_reason_and_author():
    result = _pin(_VALID, reason="do not touch")
    entry = result.pinned[0]
    assert entry.reason == "do not touch"
    assert entry.pinned_by == "tester"
    assert entry.pinned_at == _NOW


def test_pinned_expression_is_pinned():
    entry = PinnedExpression(_VALID, "r", _NOW, "u")
    assert entry.is_pinned() is True


# --- formatters ---

def test_format_pinned_entry_contains_expression():
    entry = PinnedExpression(_VALID, "freeze this", _NOW, "admin")
    text = format_pinned_entry(entry)
    assert _VALID in text


def test_format_pinned_entry_contains_reason():
    entry = PinnedExpression(_VALID, "freeze this", _NOW, "admin")
    text = format_pinned_entry(entry)
    assert "freeze this" in text


def test_format_pinned_entry_contains_author():
    entry = PinnedExpression(_VALID, "r", _NOW, "admin")
    text = format_pinned_entry(entry)
    assert "admin" in text


def test_format_pin_result_shows_pinned_count():
    result = _pin(_VALID, _VALID2)
    text = format_pin_result(result)
    assert "2" in text


def test_format_pin_result_shows_invalid_section():
    result = _pin(_INVALID)
    text = format_pin_result(result)
    assert "invalid" in text.lower()
    assert _INVALID in text


def test_format_pin_result_no_pinned_message():
    result = _pin(_INVALID)
    text = format_pin_result(result)
    assert "No expressions were pinned" in text


def test_format_pinned_list_empty():
    text = format_pinned_list([])
    assert "No expressions" in text


def test_format_pinned_list_contains_header():
    entries = [PinnedExpression(_VALID, "r", _NOW, "u")]
    text = format_pinned_list(entries)
    assert "Pinned Expressions" in text

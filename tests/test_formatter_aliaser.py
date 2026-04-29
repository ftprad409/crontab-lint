"""Tests for crontab_lint.formatter_aliaser."""

from crontab_lint.aliaser import alias
from crontab_lint.formatter_aliaser import (
    format_alias_entry,
    format_alias_lookup,
    format_alias_result,
)


def _result(*pairs):
    return alias(list(pairs))


def test_format_entry_valid_contains_checkmark():
    result = _result(("nightly", "0 0 * * *"))
    text = format_alias_entry(result.entries[0])
    assert "\u2713" in text


def test_format_entry_invalid_contains_cross():
    result = alias([("bad", "99 99 99 99 99")], allow_invalid=True)
    text = format_alias_entry(result.entries[0])
    assert "\u2717" in text


def test_format_entry_contains_alias_and_expression():
    result = _result(("backup", "0 2 * * *"))
    text = format_alias_entry(result.entries[0])
    assert "backup" in text
    assert "0 2 * * *" in text


def test_format_entry_shows_comment():
    result = alias([("weekly", "0 0 * * 0", "runs on Sunday")])
    text = format_alias_entry(result.entries[0])
    assert "runs on Sunday" in text


def test_format_entry_no_comment_no_hash():
    result = _result(("hourly", "0 * * * *"))
    text = format_alias_entry(result.entries[0])
    assert "#" not in text


def test_format_result_header():
    result = _result(("a", "* * * * *"))
    text = format_alias_result(result)
    assert "Cron Aliases" in text


def test_format_result_contains_total():
    result = _result(("a", "* * * * *"), ("b", "0 0 * * *"))
    text = format_alias_result(result)
    assert "Total" in text
    assert "2" in text


def test_format_result_lists_skipped():
    result = alias([("bad", "99 99 99 99 99")])
    text = format_alias_result(result)
    assert "Skipped" in text
    assert "bad" in text


def test_format_result_empty_aliases_message():
    result = alias([])
    text = format_alias_result(result)
    assert "no aliases" in text


def test_format_lookup_found():
    result = _result(("daily", "0 0 * * *"))
    text = format_alias_lookup("daily", result)
    assert "daily" in text
    assert "0 0 * * *" in text


def test_format_lookup_not_found():
    result = _result(("daily", "0 0 * * *"))
    text = format_alias_lookup("missing", result)
    assert "not found" in text

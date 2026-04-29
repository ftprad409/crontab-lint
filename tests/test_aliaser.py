"""Tests for crontab_lint.aliaser."""

import pytest

from crontab_lint.aliaser import AliasEntry, AliasResult, alias


def test_alias_returns_alias_result():
    result = alias([("backup", "0 2 * * *")])
    assert isinstance(result, AliasResult)


def test_alias_valid_expression_is_registered():
    result = alias([("backup", "0 2 * * *")])
    assert result.total_aliases == 1
    assert result.entries[0].alias == "backup"
    assert result.entries[0].expression == "0 2 * * *"
    assert result.entries[0].valid is True


def test_alias_invalid_expression_skipped_by_default():
    result = alias([("bad", "99 99 99 99 99")])
    assert result.total_aliases == 0
    assert "bad" in result.skipped


def test_alias_invalid_expression_allowed_when_flag_set():
    result = alias([("bad", "99 99 99 99 99")], allow_invalid=True)
    assert result.total_aliases == 1
    assert result.entries[0].valid is False


def test_alias_duplicate_alias_skipped():
    result = alias([("nightly", "0 0 * * *"), ("nightly", "30 1 * * *")])
    assert result.total_aliases == 1
    assert "nightly" in result.skipped


def test_alias_comment_stored():
    result = alias([("weekly", "0 0 * * 0", "every Sunday")])
    assert result.entries[0].comment == "every Sunday"


def test_alias_resolve_returns_entry():
    result = alias([("hourly", "0 * * * *")])
    entry = result.resolve("hourly")
    assert entry is not None
    assert entry.expression == "0 * * * *"


def test_alias_resolve_missing_returns_none():
    result = alias([("hourly", "0 * * * *")])
    assert result.resolve("nonexistent") is None


def test_alias_as_dict():
    result = alias([("a", "0 1 * * *"), ("b", "0 2 * * *")])
    d = result.as_dict()
    assert d == {"a": "0 1 * * *", "b": "0 2 * * *"}


def test_alias_empty_name_skipped():
    result = alias([("  ", "0 * * * *")])
    assert result.total_aliases == 0


def test_alias_strips_whitespace_from_expression():
    result = alias([("trim", "  0 * * * *  ")])
    assert result.entries[0].expression == "0 * * * *"


def test_alias_multiple_valid_entries():
    pairs = [("a", "* * * * *"), ("b", "0 0 * * *"), ("c", "0 12 * * 1")]
    result = alias(pairs)
    assert result.total_aliases == 3
    assert result.total_skipped == 0

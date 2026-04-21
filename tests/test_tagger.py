"""Tests for crontab_lint.tagger."""

import pytest
from crontab_lint.tagger import tag, TaggedExpression, _build_tags, _extract_inline_comment


def test_tag_valid_expression():
    entries = tag(["* * * * *"])
    assert len(entries) == 1
    assert entries[0].valid is True
    assert "every-minute" in entries[0].tags


def test_tag_invalid_expression():
    entries = tag(["99 * * * *"])
    assert len(entries) == 1
    assert entries[0].valid is False
    assert "invalid" in entries[0].tags


def test_tag_skips_comments():
    entries = tag(["# this is a comment", "0 * * * *"])
    assert len(entries) == 1
    assert entries[0].expression == "0 * * * *"


def test_tag_skips_blank_lines():
    entries = tag(["", "   ", "0 0 * * *"])
    assert len(entries) == 1


def test_tag_inline_comment_extracted():
    entries = tag(["0 9 * * 1-5  # morning standup"])
    assert len(entries) == 1
    assert entries[0].comment == "morning standup"
    assert entries[0].expression == "0 9 * * 1-5"


def test_tag_frequent():
    tags = _build_tags("*/5 * * * *")
    assert "frequent" in tags


def test_tag_half_hourly():
    tags = _build_tags("*/30 * * * *")
    assert "half-hourly" in tags


def test_tag_quarter_hourly():
    tags = _build_tags("*/15 * * * *")
    assert "quarter-hourly" in tags


def test_extract_inline_comment_no_comment():
    expr, comment = _extract_inline_comment("0 0 * * *")
    assert expr == "0 0 * * *"
    assert comment is None


def test_extract_inline_comment_with_comment():
    expr, comment = _extract_inline_comment("0 0 * * * # daily midnight")
    assert expr == "0 0 * * *"
    assert comment == "daily midnight"


def test_tag_multiple_expressions():
    lines = ["* * * * *", "0 0 * * *", "invalid expr"]
    entries = tag(lines)
    assert len(entries) == 3
    valid_flags = [e.valid for e in entries]
    assert valid_flags == [True, True, False]

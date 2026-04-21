"""Tests for crontab_lint.formatter_tagger."""

import pytest
from crontab_lint.tagger import tag
from crontab_lint.formatter_tagger import format_tagged_line, format_tag_report


def _single(line: str):
    entries = tag([line])
    assert len(entries) == 1
    return entries[0]


def test_format_valid_line_contains_checkmark():
    entry = _single("* * * * *")
    result = format_tagged_line(entry)
    assert "✔" in result


def test_format_invalid_line_contains_cross():
    entry = _single("99 * * * *")
    result = format_tagged_line(entry)
    assert "✘" in result


def test_format_line_contains_tags():
    entry = _single("* * * * *")
    result = format_tagged_line(entry)
    assert "Tags:" in result
    assert "every-minute" in result


def test_format_line_shows_inline_comment():
    entry = _single("0 9 * * * # wake up")
    result = format_tagged_line(entry)
    assert "wake up" in result


def test_format_tag_report_header():
    entries = tag(["* * * * *"])
    report = format_tag_report(entries)
    assert "Crontab Tag Report" in report


def test_format_tag_report_tag_index():
    entries = tag(["* * * * *", "0 0 * * *"])
    report = format_tag_report(entries)
    assert "Tag Index:" in report


def test_format_tag_report_empty():
    report = format_tag_report([])
    assert "No expressions" in report


def test_format_tag_report_counts_tags():
    entries = tag(["* * * * *", "*/5 * * * *"])
    report = format_tag_report(entries)
    assert "expression" in report

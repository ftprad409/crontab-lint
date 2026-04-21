"""Tests for crontab_lint.validator_report."""

import pytest
from crontab_lint.validator_report import build_report, ValidationReport, ValidationEntry


VALID_LINES = [
    "* * * * *",
    "0 9 * * 1",
    "30 18 1 * *",
]

MIXED_LINES = [
    "# daily backup",
    "0 2 * * *",
    "",
    "not a cron",
    "@daily",
]


def test_build_report_returns_validation_report():
    report = build_report(VALID_LINES)
    assert isinstance(report, ValidationReport)


def test_build_report_counts_valid():
    report = build_report(VALID_LINES)
    assert report.valid_count == 3
    assert report.invalid_count == 0


def test_build_report_entries_count_matches_lines():
    report = build_report(VALID_LINES)
    assert report.total == len(VALID_LINES)


def test_build_report_skips_comments_and_blanks():
    report = build_report(MIXED_LINES)
    assert report.skipped_count == 2  # comment + blank


def test_build_report_detects_invalid():
    report = build_report(MIXED_LINES)
    assert report.invalid_count == 1  # "not a cron"


def test_build_report_valid_entry_has_explanation():
    report = build_report(["0 9 * * 1"])
    entry = report.entries[0]
    assert entry.valid is True
    assert entry.explanation is not None
    assert isinstance(entry.explanation, str)
    assert len(entry.explanation) > 0


def test_build_report_invalid_entry_has_error():
    report = build_report(["not a cron"])
    entry = report.entries[0]
    assert entry.valid is False
    assert entry.error is not None
    assert "not a cron" in entry.error or "Invalid" in entry.error


def test_build_report_comment_entry_flags():
    report = build_report(["# this is a comment"])
    entry = report.entries[0]
    assert entry.is_comment is True
    assert entry.is_blank is False
    assert entry.valid is False


def test_build_report_blank_entry_flags():
    report = build_report([""])
    entry = report.entries[0]
    assert entry.is_blank is True
    assert entry.is_comment is False


def test_build_report_line_numbers_are_1_indexed():
    report = build_report(["* * * * *", "0 0 * * *"])
    assert report.entries[0].line_number == 1
    assert report.entries[1].line_number == 2


def test_build_report_normalizes_at_daily():
    report = build_report(["@daily"])
    entry = report.entries[0]
    assert entry.valid is True
    assert entry.normalized == "0 0 * * *"


def test_build_report_empty_input():
    report = build_report([])
    assert report.total == 0
    assert report.valid_count == 0
    assert report.invalid_count == 0

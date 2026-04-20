"""Tests for the formatter_annotator module."""

import pytest
from crontab_lint.annotator import annotate
from crontab_lint.formatter_annotator import (
    format_annotated_line,
    format_annotation_report,
)


def _annotate_single(line: str):
    return annotate([line])[0]


def test_format_valid_line_contains_checkmark():
    line = _annotate_single("*/5 * * * *")
    result = format_annotated_line(line)
    assert "\u2713" in result


def test_format_invalid_line_contains_cross():
    line = _annotate_single("99 99 99 99 99")
    result = format_annotated_line(line)
    assert "\u2717" in result
    assert "ERROR" in result


def test_format_comment_line():
    line = _annotate_single("# my comment")
    result = format_annotated_line(line)
    assert "my comment" in result
    assert "\u2713" not in result
    assert "\u2717" not in result


def test_format_blank_line_returns_empty():
    line = _annotate_single("")
    result = format_annotated_line(line)
    assert result == ""


def test_format_valid_line_contains_explanation():
    line = _annotate_single("0 9 * * 1")
    result = format_annotated_line(line)
    assert "#" in result


def test_report_contains_header():
    lines = annotate(["*/5 * * * *"])
    report = format_annotation_report(lines)
    assert "Annotation Report" in report


def test_report_contains_summary_counts():
    lines = annotate(["*/5 * * * *", "99 99 99 99 99"])
    report = format_annotation_report(lines)
    assert "Total: 2" in report
    assert "Valid: 1" in report
    assert "Invalid: 1" in report


def test_report_skips_blank_lines_in_output():
    lines = annotate(["*/5 * * * *", "", "0 0 * * *"])
    report = format_annotation_report(lines)
    # blank lines produce empty strings, should not add noise
    assert "Total: 2" in report

"""Tests for format_summary in crontab_lint.formatter."""
from crontab_lint.summarizer import summarize, CrontabSummary
from crontab_lint.formatter import format_summary


def test_format_summary_contains_totals():
    summary = CrontabSummary(total=5, valid=4, invalid=1, conflict_count=2)
    output = format_summary(summary)
    assert "5" in output
    assert "4" in output
    assert "1" in output
    assert "2" in output


def test_format_summary_lists_invalid():
    summary = CrontabSummary(
        total=2, valid=1, invalid=1,
        invalid_expressions=["99 99 * * *"]
    )
    output = format_summary(summary)
    assert "99 99 * * *" in output


def test_format_summary_no_invalid_section_when_clean():
    summary = CrontabSummary(total=1, valid=1, invalid=0)
    output = format_summary(summary)
    assert "Invalid entries" not in output


def test_format_summary_header():
    summary = CrontabSummary()
    output = format_summary(summary)
    assert "Summary" in output


def test_format_summary_from_real_data():
    summary = summarize(["0 9 * * 1-5", "30 18 * * *", "bad expr"])
    output = format_summary(summary)
    assert "Valid" in output
    assert "Invalid" in output

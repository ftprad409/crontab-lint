"""Tests for crontab_lint.summarizer."""
import pytest
from crontab_lint.summarizer import summarize


VALID_A = "0 9 * * 1-5"
VALID_B = "0 9 * * 1-5"  # duplicate — will conflict
VALID_C = "30 18 * * *"
INVALID = "99 99 99 99 99"


def test_summary_counts_valid_and_invalid():
    summary = summarize([VALID_A, VALID_C, INVALID])
    assert summary.total == 3
    assert summary.valid == 2
    assert summary.invalid == 1


def test_summary_invalid_expressions_listed():
    summary = summarize([INVALID, VALID_A])
    assert INVALID in summary.invalid_expressions


def test_summary_conflict_detected():
    summary = summarize([VALID_A, VALID_B])
    assert summary.conflict_count >= 1


def test_summary_no_conflicts():
    summary = summarize([VALID_A, VALID_C])
    assert summary.conflict_count == 0


def test_summary_skips_comments_and_blanks():
    lines = ["# this is a comment", "", VALID_A]
    summary = summarize(lines)
    assert summary.total == 1
    assert summary.valid == 1


def test_summary_empty_input():
    summary = summarize([])
    assert summary.total == 0
    assert summary.valid == 0
    assert summary.invalid == 0

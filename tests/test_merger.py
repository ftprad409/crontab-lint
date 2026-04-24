"""Tests for crontab_lint.merger."""

import pytest

from crontab_lint.merger import merge, MergeResult


CRONTAB_A = """# daily backup
0 2 * * * /usr/bin/backup
*/5 * * * * /usr/bin/poll
"""

CRONTAB_B = """# nightly cleanup
0 2 * * * /usr/bin/backup
30 6 * * 1 /usr/bin/weekly
"""


def test_merge_returns_merge_result():
    result = merge([CRONTAB_A])
    assert isinstance(result, MergeResult)


def test_merge_deduplicates_identical_expressions():
    result = merge([CRONTAB_A, CRONTAB_B])
    expressions = [l for l in result.lines if not l.startswith("#")]
    assert expressions.count("0 2 * * * /usr/bin/backup") == 1


def test_merge_duplicate_count():
    result = merge([CRONTAB_A, CRONTAB_B])
    assert result.duplicate_count == 1


def test_merge_preserves_comments():
    result = merge([CRONTAB_A, CRONTAB_B])
    comments = [l for l in result.lines if l.startswith("#")]
    assert len(comments) == 2


def test_merge_comment_count():
    result = merge([CRONTAB_A, CRONTAB_B])
    assert result.comment_count == 2


def test_merge_skips_blank_lines():
    result = merge([CRONTAB_A])
    assert all(l.strip() != "" for l in result.lines)


def test_merge_records_sources():
    result = merge([CRONTAB_A, CRONTAB_B])
    assert len(result.sources) == 2


def test_merge_invalid_expression_included_by_default():
    bad = "not a valid cron\n0 2 * * * /bin/ok"
    result = merge([bad])
    assert result.invalid_count == 1
    assert any("not a valid" in l for l in result.lines)


def test_merge_skip_invalid_excludes_bad_lines():
    bad = "not a valid cron\n0 2 * * * /bin/ok"
    result = merge([bad], skip_invalid=True)
    assert result.invalid_count == 1
    assert all("not a valid" not in l for l in result.lines)


def test_merge_normalizes_at_daily():
    crontab = "@daily /bin/cleanup\n"
    result = merge([crontab], normalize_expressions=True)
    expressions = [l for l in result.lines if not l.startswith("#")]
    assert any("0 0 * * *" in e for e in expressions)


def test_merge_no_normalization_preserves_original():
    crontab = "@daily /bin/cleanup\n"
    result = merge([crontab], normalize_expressions=False)
    assert any("@daily" in l for l in result.lines)


def test_merge_three_sources_all_unique():
    a = "0 1 * * * /bin/a"
    b = "0 2 * * * /bin/b"
    c = "0 3 * * * /bin/c"
    result = merge([a, b, c])
    assert result.duplicate_count == 0
    assert len([l for l in result.lines if not l.startswith("#")]) == 3

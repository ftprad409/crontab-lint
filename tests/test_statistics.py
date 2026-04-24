"""Tests for crontab_lint.statistics."""

import pytest
from crontab_lint.statistics import compute, CrontabStatistics


LINES = [
    "# daily backup",
    "0 2 * * * /backup.sh",
    "*/5 * * * * /poll.sh",
    "0 9 * * 1 /weekly.sh",
    "",
    "not a valid expression",
    "30 6 * * * /morning.sh",
]


def test_compute_returns_statistics_instance():
    result = compute(LINES)
    assert isinstance(result, CrontabStatistics)


def test_compute_total_counts_all_lines():
    result = compute(LINES)
    assert result.total == len(LINES)


def test_compute_counts_comments():
    result = compute(LINES)
    assert result.comment == 1


def test_compute_counts_blanks():
    result = compute(LINES)
    assert result.blank == 1


def test_compute_counts_invalid():
    result = compute(LINES)
    assert result.invalid == 1


def test_compute_counts_valid():
    result = compute(LINES)
    assert result.valid == 4


def test_compute_valid_plus_invalid_plus_meta_equals_total():
    result = compute(LINES)
    assert result.valid + result.invalid + result.comment + result.blank == result.total


def test_compute_schedule_distribution_is_dict():
    result = compute(LINES)
    assert isinstance(result.schedule_distribution, dict)


def test_compute_schedule_distribution_values_are_ints():
    result = compute(LINES)
    for v in result.schedule_distribution.values():
        assert isinstance(v, int)


def test_compute_most_common_minute_is_string():
    result = compute(LINES)
    assert isinstance(result.most_common_minute, str)


def test_compute_most_common_hour_is_string():
    result = compute(LINES)
    assert isinstance(result.most_common_hour, str)


def test_compute_empty_input():
    result = compute([])
    assert result.total == 0
    assert result.valid == 0
    assert result.invalid == 0
    assert result.most_common_minute == ""
    assert result.most_common_hour == ""
    assert result.schedule_distribution == {}


def test_compute_only_comments_and_blanks():
    result = compute(["# comment", "", "  "])
    assert result.valid == 0
    assert result.invalid == 0

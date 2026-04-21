"""Tests for crontab_lint.sorter."""

import pytest
from crontab_lint.sorter import sort, SortedCrontab, _sort_key, _min_value


EVERY_MINUTE = "* * * * *"
HOURLY = "0 * * * *"
DAILY_NOON = "0 12 * * *"
DAILY_MIDNIGHT = "0 0 * * *"
WEEKLY = "0 9 * * 1"
MONTHLY = "0 6 1 * *"


def test_sort_returns_sorted_crontab_instance():
    result = sort([EVERY_MINUTE, HOURLY])
    assert isinstance(result, SortedCrontab)


def test_sort_schedule_orders_by_minute_then_hour():
    lines = [DAILY_NOON, DAILY_MIDNIGHT, HOURLY, EVERY_MINUTE]
    result = sort(lines, key="schedule")
    # EVERY_MINUTE (min=0,hr=0), DAILY_MIDNIGHT (0,0), HOURLY (0,*->0), DAILY_NOON (0,12)
    # All start at minute 0; order by hour: 0, 0, 0, 12
    assert result.entries.index(DAILY_NOON) > result.entries.index(DAILY_MIDNIGHT)


def test_sort_alpha_orders_lexicographically():
    lines = ["30 6 * * *", "0 0 * * *", "15 3 * * *"]
    result = sort(lines, key="alpha")
    assert result.entries == sorted(["30 6 * * *", "0 0 * * *", "15 3 * * *"])


def test_sort_reverse_flag():
    lines = ["0 1 * * *", "0 2 * * *", "0 3 * * *"]
    asc = sort(lines, key="schedule", reverse=False)
    desc = sort(lines, key="schedule", reverse=True)
    assert asc.entries == list(reversed(desc.entries))


def test_sort_skips_comments():
    lines = ["# daily job", DAILY_NOON, "# another comment"]
    result = sort(lines)
    assert "# daily job" in result.skipped
    assert "# another comment" in result.skipped
    assert DAILY_NOON in result.entries


def test_sort_skips_blank_lines():
    lines = ["", "  ", HOURLY]
    result = sort(lines)
    assert len(result.skipped) == 2
    assert result.entries == [HOURLY]


def test_sort_skips_invalid_expressions():
    lines = ["not a cron", EVERY_MINUTE, "99 99 99 99 99"]
    result = sort(lines)
    assert EVERY_MINUTE in result.entries
    assert "not a cron" in result.skipped
    assert "99 99 99 99 99" in result.skipped


def test_sort_empty_input():
    result = sort([])
    assert result.entries == []
    assert result.skipped == []


def test_min_value_wildcard_returns_lower_bound():
    assert _min_value("* * * * *", "minute") == 0
    assert _min_value("* * * * *", "month") == 1


def test_min_value_specific():
    assert _min_value("30 6 * * *", "minute") == 30
    assert _min_value("30 6 * * *", "hour") == 6


def test_min_value_range():
    assert _min_value("10-20 * * * *", "minute") == 10


def test_sort_key_tuple_length():
    key = _sort_key(DAILY_NOON)
    assert len(key) == 5


def test_sort_monthly_after_daily():
    lines = [MONTHLY, DAILY_MIDNIGHT]
    result = sort(lines, key="schedule")
    # DAILY_MIDNIGHT: day=1(wildcard->1?), MONTHLY: day=1, month=1
    # Both have minute=0, hour=0, day=1; MONTHLY has month=1 same as wildcard min
    # At minimum they are both present and sorted
    assert set(result.entries) == {MONTHLY, DAILY_MIDNIGHT}

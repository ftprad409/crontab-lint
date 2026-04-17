"""Tests for conflict_detector module."""

import pytest
from crontab_lint.conflict_detector import detect_conflicts, _expand_field, _expressions_overlap
from crontab_lint.parser import parse


def test_expand_wildcard():
    assert _expand_field("*", 0, 5) == {0, 1, 2, 3, 4, 5}


def test_expand_range():
    assert _expand_field("1-3", 0, 59) == {1, 2, 3}


def test_expand_step():
    assert _expand_field("*/15", 0, 59) == {0, 15, 30, 45}


def test_expand_list():
    assert _expand_field("1,3,5", 0, 59) == {1, 3, 5}


def test_no_conflicts():
    exprs = ["0 9 * * 1", "0 10 * * 2"]
    assert detect_conflicts(exprs) == []


def test_identical_expressions_conflict():
    exprs = ["0 9 * * *", "0 9 * * *"]
    conflicts = detect_conflicts(exprs)
    assert len(conflicts) == 1
    assert conflicts[0].index_a == 0
    assert conflicts[0].index_b == 1


def test_partial_overlap_conflict():
    exprs = ["0 9 * * 1-5", "0 9 * * 3"]
    conflicts = detect_conflicts(exprs)
    assert len(conflicts) == 1


def test_invalid_expression_skipped():
    exprs = ["bad expr", "0 9 * * *"]
    conflicts = detect_conflicts(exprs)
    assert conflicts == []


def test_multiple_conflicts():
    exprs = ["* * * * *", "0 9 * * *", "0 9 1 * *"]
    conflicts = detect_conflicts(exprs)
    assert len(conflicts) >= 2

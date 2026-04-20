"""Tests for the annotator module."""

import pytest
from crontab_lint.annotator import annotate, AnnotatedLine


VALID_EXPR = "*/5 * * * *"
INVALID_EXPR = "99 99 99 99 99"


def test_annotate_valid_expression():
    lines = [VALID_EXPR]
    result = annotate(lines)
    assert len(result) == 1
    assert result[0].is_valid is True
    assert result[0].explanation != ""
    assert result[0].error == ""
    assert result[0].line_number == 1


def test_annotate_invalid_expression():
    lines = [INVALID_EXPR]
    result = annotate(lines)
    assert len(result) == 1
    assert result[0].is_valid is False
    assert result[0].error != ""


def test_annotate_comment_line():
    lines = ["# this is a comment"]
    result = annotate(lines)
    assert result[0].is_comment is True
    assert result[0].is_valid is True
    assert result[0].explanation == ""


def test_annotate_blank_line():
    lines = [""]
    result = annotate(lines)
    assert result[0].is_blank is True
    assert result[0].is_valid is True


def test_annotate_mixed_lines():
    lines = ["# comment", "", VALID_EXPR, INVALID_EXPR]
    result = annotate(lines)
    assert len(result) == 4
    assert result[0].is_comment is True
    assert result[1].is_blank is True
    assert result[2].is_valid is True
    assert result[3].is_valid is False


def test_annotate_line_numbers():
    lines = ["# header", VALID_EXPR, INVALID_EXPR]
    result = annotate(lines)
    assert result[0].line_number == 1
    assert result[1].line_number == 2
    assert result[2].line_number == 3


def test_annotate_expression_stored():
    lines = ["  " + VALID_EXPR + "  "]
    result = annotate(lines)
    assert result[0].expression == VALID_EXPR


def test_annotate_empty_input():
    result = annotate([])
    assert result == []

"""Tests for crontab_lint.highlighter."""

from __future__ import annotations

import pytest

from crontab_lint.highlighter import (
    HighlightedLine,
    highlight,
    highlight_expression,
)

_RESET = "\033[0m"
_RED = "\033[31m"
_COMMENT = "\033[90m"


# ---------------------------------------------------------------------------
# highlight_expression
# ---------------------------------------------------------------------------

class TestHighlightExpression:
    def test_valid_expression_contains_reset_codes(self):
        result = highlight_expression("* * * * * /bin/true")
        assert _RESET in result

    def test_valid_expression_contains_command(self):
        result = highlight_expression("0 6 * * 1 /usr/bin/backup")
        assert "/usr/bin/backup" in result

    def test_invalid_expression_rendered_in_red(self):
        result = highlight_expression("not a cron expression")
        assert result.startswith(_RED)

    def test_valid_expression_not_red(self):
        result = highlight_expression("30 8 * * * echo hi")
        assert not result.startswith(_RED)

    def test_five_field_expression_no_command(self):
        # Five fields only (no command) – should still be coloured, not red
        result = highlight_expression("*/5 * * * *")
        assert _RED not in result


# ---------------------------------------------------------------------------
# highlight (list of lines)
# ---------------------------------------------------------------------------

class TestHighlight:
    def test_returns_list_of_highlighted_lines(self):
        lines = ["* * * * * /bin/true"]
        result = highlight(lines)
        assert isinstance(result, list)
        assert all(isinstance(h, HighlightedLine) for h in result)

    def test_blank_line_not_expression(self):
        result = highlight([""])
        assert result[0].is_expression is False
        assert result[0].rendered == ""

    def test_comment_line_not_expression(self):
        result = highlight(["# every minute"])
        hl = result[0]
        assert hl.is_expression is False
        assert _COMMENT in hl.rendered

    def test_valid_expression_flagged_as_valid(self):
        result = highlight(["0 12 * * * /bin/echo"])
        hl = result[0]
        assert hl.is_expression is True
        assert hl.is_valid is True

    def test_invalid_expression_flagged_as_invalid(self):
        result = highlight(["99 99 99 99 99 bad"])
        hl = result[0]
        assert hl.is_expression is True
        assert hl.is_valid is False

    def test_mixed_lines_correct_count(self):
        lines = [
            "# header",
            "",
            "*/10 * * * * /bin/check",
            "bad line here",
        ]
        result = highlight(lines)
        assert len(result) == 4

    def test_raw_field_preserved(self):
        raw = "5 4 * * 0 /usr/bin/weekly"
        result = highlight([raw])
        assert result[0].raw == raw

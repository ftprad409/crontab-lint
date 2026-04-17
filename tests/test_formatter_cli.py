"""Tests for formatter and CLI integration."""

import pytest
from crontab_lint.formatter import format_conflicts, format_validation_result, format_lint_report
from crontab_lint.conflict_detector import Conflict
from crontab_lint.cli import main


def test_format_no_conflicts():
    assert "No conflicts" in format_conflicts([])


def test_format_with_conflict():
    c = Conflict(0, 1, "0 9 * * *", "0 9 * * *", "Overlap")
    output = format_conflicts([c])
    assert "0 9 * * *" in output
    assert "Overlap" in output


def test_format_valid_result():
    out = format_validation_result("0 9 * * *", True, "At 09:00")
    assert "VALID" in out
    assert "At 09:00" in out


def test_format_invalid_result():
    out = format_validation_result("bad", False)
    assert "INVALID" in out


def test_format_lint_report_contains_sections():
    results = [{"expression": "0 9 * * *", "valid": True, "explanation": "At 09:00"}]
    conflicts = []
    report = format_lint_report(results, conflicts)
    assert "Validation Results" in report
    assert "Conflict Detection" in report


def test_cli_valid_expression(capsys):
    main(["0 9 * * *"])
    captured = capsys.readouterr()
    assert "VALID" in captured.out


def test_cli_invalid_expression(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["bad expression here"])
    assert exc.value.code == 1


def test_cli_no_expressions(capsys):
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 0

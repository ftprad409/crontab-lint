"""Tests for crontab_lint.exporter."""

import json
import pytest
from crontab_lint.summarizer import CrontabSummary
from crontab_lint.conflict_detector import Conflict
from crontab_lint.exporter import export_json, export_csv, export


def _make_summary(**kwargs):
    defaults = dict(total=3, valid_count=2, invalid_count=1,
                    invalid_expressions=["bad expr"], conflict_count=1)
    defaults.update(kwargs)
    return CrontabSummary(**defaults)


def _make_conflict():
    return Conflict(
        expression_a="* * * * *",
        expression_b="*/1 * * * *",
        reason="Overlapping schedules",
    )


def test_export_json_structure():
    summary = _make_summary()
    conflicts = [_make_conflict()]
    result = json.loads(export_json(summary, conflicts))
    assert result["total"] == 3
    assert result["valid"] == 2
    assert result["invalid"] == 1
    assert result["invalid_expressions"] == ["bad expr"]
    assert len(result["conflicts"]) == 1
    assert result["conflicts"][0]["reason"] == "Overlapping schedules"


def test_export_json_no_conflicts():
    summary = _make_summary(conflict_count=0)
    result = json.loads(export_json(summary, []))
    assert result["conflicts"] == []


def test_export_csv_header_comment():
    summary = _make_summary()
    conflicts = [_make_conflict()]
    csv_out = export_csv(summary, conflicts)
    assert csv_out.startswith("# total=3")
    assert "valid=2" in csv_out


def test_export_csv_rows():
    summary = _make_summary()
    conflicts = [_make_conflict()]
    csv_out = export_csv(summary, conflicts)
    assert "expression_a" in csv_out
    assert "* * * * *" in csv_out
    assert "Overlapping schedules" in csv_out


def test_export_dispatch_json():
    summary = _make_summary()
    result = export("json", summary, [])
    assert json.loads(result)["total"] == 3


def test_export_dispatch_csv():
    summary = _make_summary()
    result = export("csv", summary, [])
    assert "expression_a" in result


def test_export_unsupported_format():
    with pytest.raises(ValueError, match="Unsupported export format"):
        export("xml", _make_summary(), [])

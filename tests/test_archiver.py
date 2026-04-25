"""Tests for crontab_lint.archiver and crontab_lint.formatter_archiver."""

import json
from pathlib import Path

import pytest

from crontab_lint.archiver import (
    ArchivedEntry,
    ArchiveResult,
    archive,
    load_archive,
    save_archive,
)
from crontab_lint.formatter_archiver import (
    format_archive_result,
    format_archive_summary,
    format_archived_entry,
)


VALID_EXPR = "*/5 * * * * /usr/bin/backup"
INVALID_EXPR = "99 99 99 99 99 oops"


# --- archiver ---

def test_archive_returns_archive_result():
    result = archive([VALID_EXPR])
    assert isinstance(result, ArchiveResult)


def test_archive_valid_expression_marked_valid():
    result = archive([VALID_EXPR])
    assert result.entries[0].valid is True


def test_archive_invalid_expression_marked_invalid():
    result = archive([INVALID_EXPR])
    assert result.entries[0].valid is False


def test_archive_skips_comments_and_blanks():
    lines = ["# comment", "", VALID_EXPR]
    result = archive(lines)
    assert result.total == 1


def test_archive_counts():
    result = archive([VALID_EXPR, INVALID_EXPR])
    assert result.total == 2
    assert result.valid_count == 1
    assert result.invalid_count == 1


def test_archive_label_propagated():
    result = archive([VALID_EXPR], label="prod")
    assert result.entries[0].label == "prod"


def test_archive_source_stored():
    result = archive([VALID_EXPR], source="crontab.txt")
    assert result.source == "crontab.txt"


def test_archived_entry_has_timestamp():
    result = archive([VALID_EXPR])
    ts = result.entries[0].archived_at
    assert "T" in ts  # ISO format check


def test_save_and_load_roundtrip(tmp_path: Path):
    result = archive([VALID_EXPR, INVALID_EXPR], source="test", label="ci")
    dest = tmp_path / "archive.json"
    save_archive(result, dest)
    loaded = load_archive(dest)
    assert loaded.total == result.total
    assert loaded.source == "test"
    assert loaded.entries[0].label == "ci"
    assert loaded.entries[0].valid is True


def test_save_produces_valid_json(tmp_path: Path):
    result = archive([VALID_EXPR])
    dest = tmp_path / "archive.json"
    save_archive(result, dest)
    data = json.loads(dest.read_text())
    assert "entries" in data


# --- formatter ---

def test_format_archived_entry_contains_expression():
    entry = ArchivedEntry(expression=VALID_EXPR, archived_at="2024-01-01T00:00:00+00:00")
    line = format_archived_entry(entry)
    assert VALID_EXPR in line


def test_format_archived_entry_valid_checkmark():
    entry = ArchivedEntry(expression=VALID_EXPR, archived_at="2024-01-01T00:00:00+00:00", valid=True)
    assert "\u2713" in format_archived_entry(entry)


def test_format_archived_entry_invalid_cross():
    entry = ArchivedEntry(expression=INVALID_EXPR, archived_at="2024-01-01T00:00:00+00:00", valid=False)
    assert "\u2717" in format_archived_entry(entry)


def test_format_archive_result_contains_header():
    result = archive([VALID_EXPR], source="myfile")
    report = format_archive_result(result)
    assert "Archive Report" in report
    assert "myfile" in report


def test_format_archive_result_contains_totals():
    result = archive([VALID_EXPR, INVALID_EXPR])
    report = format_archive_result(result)
    assert "Total: 2" in report


def test_format_archive_result_empty():
    result = ArchiveResult()
    report = format_archive_result(result)
    assert "no expressions" in report


def test_format_archive_summary_one_liner():
    result = archive([VALID_EXPR], source="prod")
    summary = format_archive_summary(result)
    assert "Archived" in summary
    assert "prod" in summary
    assert "\n" not in summary

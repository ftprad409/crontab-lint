"""Tests for crontab_lint.cli_diff.handle_diff."""

import pytest
from pathlib import Path
from crontab_lint.cli_diff import handle_diff


OLD_CONTENT = "0 2 * * * /usr/bin/backup\n*/5 * * * * /usr/bin/monitor\n"
NEW_CONTENT = "0 3 * * * /usr/bin/backup\n*/5 * * * * /usr/bin/monitor\n0 0 * * * /usr/bin/cleanup\n"


@pytest.fixture
def old_file(tmp_path):
    p = tmp_path / "old.crontab"
    p.write_text(OLD_CONTENT)
    return str(p)


@pytest.fixture
def new_file(tmp_path):
    p = tmp_path / "new.crontab"
    p.write_text(NEW_CONTENT)
    return str(p)


@pytest.fixture
def same_file(tmp_path):
    p = tmp_path / "same.crontab"
    p.write_text(OLD_CONTENT)
    return str(p)


def test_handle_diff_returns_1_when_changes(old_file, new_file):
    code = handle_diff(old_file, new_file)
    assert code == 1


def test_handle_diff_returns_0_when_no_changes(old_file, same_file):
    code = handle_diff(old_file, same_file)
    assert code == 0


def test_handle_diff_returns_2_on_missing_old(new_file):
    code = handle_diff("nonexistent_old.crontab", new_file)
    assert code == 2


def test_handle_diff_returns_2_on_missing_new(old_file):
    code = handle_diff(old_file, "nonexistent_new.crontab")
    assert code == 2


def test_handle_diff_prints_report(old_file, new_file, capsys):
    handle_diff(old_file, new_file)
    captured = capsys.readouterr()
    assert "Crontab Diff Report" in captured.out
    assert "+" in captured.out
    assert "-" in captured.out

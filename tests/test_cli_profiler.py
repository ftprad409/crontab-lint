"""Tests for crontab_lint.cli_profiler.handle_profile."""

import io
import pytest
from pathlib import Path
from crontab_lint.cli_profiler import handle_profile


@pytest.fixture()
def crontab_file(tmp_path: Path) -> Path:
    content = "\n".join([
        "# sample crontab",
        "0 1 * * * /nightly.sh",
        "*/10 * * * * /poll.sh",
        "",
    ])
    p = tmp_path / "crontab.txt"
    p.write_text(content, encoding="utf-8")
    return p


def test_handle_profile_returns_0_on_success(crontab_file):
    out = io.StringIO()
    code = handle_profile(str(crontab_file), out=out)
    assert code == 0


def test_handle_profile_output_contains_report(crontab_file):
    out = io.StringIO()
    handle_profile(str(crontab_file), out=out)
    assert "Crontab Load Profile" in out.getvalue()


def test_handle_profile_returns_1_for_missing_file(tmp_path):
    out = io.StringIO()
    code = handle_profile(str(tmp_path / "missing.txt"), out=out)
    assert code == 1


def test_handle_profile_output_contains_busiest_hour(crontab_file):
    out = io.StringIO()
    handle_profile(str(crontab_file), out=out)
    assert "Busiest hour" in out.getvalue()


def test_handle_profile_output_contains_hourly_chart(crontab_file):
    out = io.StringIO()
    handle_profile(str(crontab_file), out=out)
    assert "Hourly load distribution" in out.getvalue()

"""Tests for templater, formatter_templater, and cli_templater."""
import pytest
from crontab_lint.templater import (
    list_templates,
    get_template,
    search_templates,
    CronTemplate,
)
from crontab_lint.formatter_templater import (
    format_template,
    format_template_list,
    format_template_search_result,
)
from crontab_lint.cli_templater import handle_template


# --- templater unit tests ---

def test_list_templates_returns_all():
    templates = list_templates()
    assert len(templates) >= 8
    assert all(isinstance(t, CronTemplate) for t in templates)


def test_list_templates_sorted_by_name():
    templates = list_templates()
    names = [t.name for t in templates]
    assert names == sorted(names)


def test_get_template_known_name():
    t = get_template("daily_midnight")
    assert t is not None
    assert t.expression == "0 0 * * *"


def test_get_template_unknown_returns_none():
    assert get_template("nonexistent_template") is None


def test_search_templates_by_tag():
    results = search_templates("maintenance")
    assert len(results) >= 2
    assert all("maintenance" in r.tags for r in results)


def test_search_templates_by_description_keyword():
    results = search_templates("midnight")
    assert any("midnight" in r.description.lower() for r in results)


def test_search_templates_no_match():
    results = search_templates("zzznomatch")
    assert results == []


# --- formatter_templater unit tests ---

def test_format_template_contains_name():
    t = get_template("every_hour")
    output = format_template(t)
    assert "every_hour" in output
    assert "0 * * * *" in output


def test_format_template_list_contains_header():
    templates = list_templates()
    output = format_template_list(templates)
    assert "Available Cron Templates" in output
    assert "Total:" in output


def test_format_template_list_empty():
    output = format_template_list([])
    assert "No templates found." in output


def test_format_search_result_with_matches():
    results = search_templates("daily")
    output = format_template_search_result("daily", results)
    assert "daily" in output.lower()
    assert "Found:" in output


def test_format_search_result_no_matches():
    output = format_template_search_result("zzz", [])
    assert "No matching templates found." in output


# --- cli_templater integration tests ---

def test_handle_template_list_returns_0(capsys):
    code = handle_template(["list"])
    assert code == 0
    captured = capsys.readouterr()
    assert "Available Cron Templates" in captured.out


def test_handle_template_get_known(capsys):
    code = handle_template(["get", "weekly_sunday"])
    assert code == 0
    captured = capsys.readouterr()
    assert "weekly_sunday" in captured.out


def test_handle_template_get_unknown(capsys):
    code = handle_template(["get", "ghost_template"])
    assert code == 1


def test_handle_template_search(capsys):
    code = handle_template(["search", "hourly"])
    assert code == 0
    captured = capsys.readouterr()
    assert "hourly" in captured.out.lower()


def test_handle_template_no_args_returns_2(capsys):
    code = handle_template([])
    assert code == 2


def test_handle_template_unknown_subcommand_returns_2(capsys):
    code = handle_template(["explode"])
    assert code == 2

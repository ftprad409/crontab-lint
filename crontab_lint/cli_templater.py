"""CLI handler for the template command."""
import sys
from typing import List

from crontab_lint.templater import list_templates, get_template, search_templates
from crontab_lint.formatter_templater import (
    format_template,
    format_template_list,
    format_template_search_result,
)


def handle_template(args: List[str]) -> int:
    """
    Handle the `crontab-lint template` subcommand.

    Usage:
      template list               -- list all templates
      template get <name>         -- show a specific template
      template search <query>     -- search templates by keyword
    """
    if not args:
        print("Usage: template <list|get|search> [args]", file=sys.stderr)
        return 2

    subcommand = args[0].lower()

    if subcommand == "list":
        templates = list_templates()
        print(format_template_list(templates))
        return 0

    if subcommand == "get":
        if len(args) < 2:
            print("Usage: template get <name>", file=sys.stderr)
            return 2
        name = args[1]
        template = get_template(name)
        if template is None:
            print(f"Template '{name}' not found.", file=sys.stderr)
            return 1
        print(format_template(template))
        return 0

    if subcommand == "search":
        if len(args) < 2:
            print("Usage: template search <query>", file=sys.stderr)
            return 2
        query = args[1]
        results = search_templates(query)
        print(format_template_search_result(query, results))
        return 0

    print(f"Unknown subcommand '{subcommand}'. Use list, get, or search.", file=sys.stderr)
    return 2

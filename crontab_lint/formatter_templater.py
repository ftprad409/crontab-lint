"""Formatters for cron template output."""
from typing import List
from crontab_lint.templater import CronTemplate


def format_template(template: CronTemplate) -> str:
    """Format a single template as a human-readable string."""
    tags = ", ".join(template.tags) if template.tags else "none"
    lines = [
        f"  Name       : {template.name}",
        f"  Expression : {template.expression}",
        f"  Description: {template.description}",
        f"  Tags       : {tags}",
    ]
    return "\n".join(lines)


def format_template_list(templates: List[CronTemplate]) -> str:
    """Format a list of templates as a report."""
    if not templates:
        return "No templates found."

    sections = ["Available Cron Templates", "=" * 40]
    for template in templates:
        sections.append(format_template(template))
        sections.append("-" * 40)

    sections.append(f"Total: {len(templates)} template(s)")
    return "\n".join(sections)


def format_template_search_result(
    query: str, templates: List[CronTemplate]
) -> str:
    """Format search results for a given query."""
    header = f"Search results for '{query}'"
    separator = "=" * len(header)
    if not templates:
        return "\n".join([header, separator, "No matching templates found."])

    sections = [header, separator]
    for template in templates:
        sections.append(format_template(template))
        sections.append("-" * 40)

    sections.append(f"Found: {len(templates)} template(s)")
    return "\n".join(sections)

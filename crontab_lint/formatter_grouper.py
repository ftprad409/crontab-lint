"""Formats grouped crontab expressions for display."""

from typing import Dict
from .grouper import CrontabGroup

LABEL_DISPLAY: Dict[str, str] = {
    "every_minute": "Every Minute",
    "every_hour": "Every Hour",
    "daily": "Daily",
    "weekly": "Weekly",
    "monthly": "Monthly",
    "yearly": "Yearly",
    "other": "Other",
    "invalid": "Invalid",
}

ORDER = ["every_minute", "every_hour", "daily", "weekly", "monthly", "yearly", "other", "invalid"]


def format_group(group: CrontabGroup) -> str:
    """Format a single CrontabGroup as a labeled section."""
    display = LABEL_DISPLAY.get(group.label, group.label.replace("_", " ").title())
    lines = [f"[{display}] ({len(group.expressions)} expression(s))"]
    for expr in group.expressions:
        lines.append(f"  {expr}")
    return "\n".join(lines)


def format_group_report(groups: Dict[str, CrontabGroup]) -> str:
    """Format all groups into a full report string."""
    if not groups:
        return "No expressions to group."

    sections = []
    for label in ORDER:
        if label in groups:
            sections.append(format_group(groups[label]))

    # Include any labels not in ORDER
    for label, grp in groups.items():
        if label not in ORDER:
            sections.append(format_group(grp))

    header = "=== Crontab Groups ==="
    return header + "\n\n" + "\n\n".join(sections)

"""Format CrontabDiff results for CLI output."""

from crontab_lint.differ import CrontabDiff

_SEP = "-" * 48


def format_diff(diff: CrontabDiff) -> str:
    lines = ["Crontab Diff Report", _SEP]

    if diff.added:
        lines.append(f"Added ({len(diff.added)}):")
        for expr in diff.added:
            lines.append(f"  + {expr}")
    else:
        lines.append("Added: none")

    lines.append("")

    if diff.removed:
        lines.append(f"Removed ({len(diff.removed)}):")
        for expr in diff.removed:
            lines.append(f"  - {expr}")
    else:
        lines.append("Removed: none")

    lines.append("")

    if diff.unchanged:
        lines.append(f"Unchanged ({len(diff.unchanged)}):")
        for expr in diff.unchanged:
            lines.append(f"    {expr}")

    lines.append("")

    if diff.invalid_in_old:
        lines.append(f"Invalid in OLD ({len(diff.invalid_in_old)}):")
        for expr in diff.invalid_in_old:
            lines.append(f"  ! {expr}")

    if diff.invalid_in_new:
        lines.append(f"Invalid in NEW ({len(diff.invalid_in_new)}):")
        for expr in diff.invalid_in_new:
            lines.append(f"  ! {expr}")

    lines.append(_SEP)
    total_changes = len(diff.added) + len(diff.removed)
    lines.append(f"Total changes: {total_changes}")

    return "\n".join(lines)

"""CLI handler for the crontab diff subcommand."""

import sys
from pathlib import Path

from crontab_lint.differ import diff
from crontab_lint.formatter_diff import format_diff


def handle_diff(old_path: str, new_path: str) -> int:
    """Read two crontab files, diff them, and print a formatted report.

    Returns an exit code: 0 if no changes, 1 if there are additions/removals,
    2 on file errors.
    """
    try:
        old_text = Path(old_path).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Error reading old file '{old_path}': {exc}", file=sys.stderr)
        return 2

    try:
        new_text = Path(new_path).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Error reading new file '{new_path}': {exc}", file=sys.stderr)
        return 2

    result = diff(old_text, new_text)
    print(format_diff(result))

    has_changes = bool(result.added or result.removed)
    return 1 if has_changes else 0

"""CLI handler for the tagging feature."""

import sys
from typing import List
from crontab_lint.tagger import tag
from crontab_lint.formatter_tagger import format_tag_report


def handle_tag(args) -> int:
    """Read a crontab file and print a tag report. Returns exit code."""
    try:
        with open(args.file, "r") as f:
            lines: List[str] = f.readlines()
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"Error reading file: {exc}", file=sys.stderr)
        return 2

    entries = tag(lines)

    if not entries:
        print("No crontab expressions found.")
        return 0

    report = format_tag_report(entries)
    print(report)

    has_invalid = any(not e.valid for e in entries)
    return 1 if has_invalid else 0

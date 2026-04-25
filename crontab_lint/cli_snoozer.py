"""CLI handler for the snooze sub-command."""
from __future__ import annotations

import argparse
import sys
from typing import List

from .snoozer import snooze
from .formatter_snoozer import format_snooze_result


def handle_snooze(args: argparse.Namespace) -> int:
    """Entry point for ``crontab-lint snooze``.

    Reads cron expressions from *args.file* (one per line) and snoozes them
    for *args.minutes* minutes, then prints the result report.

    Returns 0 on success, 1 on file-not-found or bad arguments.
    """
    try:
        duration: int = int(args.minutes)
    except (TypeError, ValueError):
        print("Error: --minutes must be a positive integer.", file=sys.stderr)
        return 1

    if duration <= 0:
        print("Error: --minutes must be greater than zero.", file=sys.stderr)
        return 1

    try:
        with open(args.file, "r", encoding="utf-8") as fh:
            lines: List[str] = [l.rstrip("\n") for l in fh]
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        return 1

    reason: str | None = getattr(args, "reason", None) or None
    result = snooze(lines, duration_minutes=duration, reason=reason)
    print(format_snooze_result(result))
    return 0

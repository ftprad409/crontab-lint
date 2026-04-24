"""CLI handler for the --profile command."""

from __future__ import annotations

import sys
from typing import List

from .profiler import profile
from .formatter_profiler import format_profile_report


def handle_profile(path: str, out=None) -> int:
    """Read *path*, compute load profile, print report.

    Returns 0 on success, 1 on I/O error.
    """
    if out is None:
        out = sys.stdout

    try:
        with open(path, "r", encoding="utf-8") as fh:
            lines: List[str] = fh.read().splitlines()
    except OSError as exc:
        print(f"Error: cannot read '{path}': {exc}", file=sys.stderr)
        return 1

    result = profile(lines)
    print(format_profile_report(result), file=out)
    return 0

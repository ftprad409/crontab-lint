"""CLI handler for the score sub-command."""
from __future__ import annotations

import sys
from pathlib import Path

from .scorer import score
from .formatter_scorer import format_score_report


def handle_score(path: str, output=None) -> int:
    """Read *path*, score every expression, print report.

    Returns 0 on success, 1 if the file cannot be read.
    """
    out = output or sys.stdout
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        print(f"Error reading file: {exc}", file=sys.stderr)
        return 1

    result = score(lines)
    print(format_score_report(result), file=out)
    return 0

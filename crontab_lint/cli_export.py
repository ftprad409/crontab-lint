"""CLI helpers for --export flag integration."""

import sys
from typing import List, Optional
from crontab_lint.summarizer import CrontabSummary
from crontab_lint.conflict_detector import Conflict
from crontab_lint.exporter import export

SUPPORTED_FORMATS = ("json", "csv")


def handle_export(
    fmt: Optional[str],
    summary: CrontabSummary,
    conflicts: List[Conflict],
    output_path: Optional[str] = None,
) -> bool:
    """If fmt is set, export results and return True; else return False.

    Writes to output_path if given, otherwise prints to stdout.
    Returns True when export was performed.
    """
    if not fmt:
        return False

    if fmt not in SUPPORTED_FORMATS:
        print(
            f"Error: unsupported export format '{fmt}'. "
            f"Choose from: {', '.join(SUPPORTED_FORMATS)}",
            file=sys.stderr,
        )
        sys.exit(1)

    content = export(fmt, summary, conflicts)

    if output_path:
        try:
            with open(output_path, "w", encoding="utf-8") as fh:
                fh.write(content)
            print(f"Exported {fmt.upper()} report to {output_path}")
        except OSError as exc:
            print(f"Error writing export file: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        print(content)

    return True

"""Export crontab lint results to JSON or CSV formats."""

import csv
import json
import io
from typing import List
from crontab_lint.summarizer import CrontabSummary
from crontab_lint.conflict_detector import Conflict

SUPPORTED_FORMATS = ("json", "csv")


def export_json(summary: CrontabSummary, conflicts: List[Conflict]) -> str:
    """Serialize summary and conflicts to a JSON string."""
    data = {
        "total": summary.total,
        "valid": summary.valid_count,
        "invalid": summary.invalid_count,
        "invalid_expressions": summary.invalid_expressions,
        "conflict_count": summary.conflict_count,
        "conflicts": [
            {
                "expression_a": c.expression_a,
                "expression_b": c.expression_b,
                "reason": c.reason,
            }
            for c in conflicts
        ],
    }
    return json.dumps(data, indent=2)


def export_csv(summary: CrontabSummary, conflicts: List[Conflict]) -> str:
    """Serialize conflicts to a CSV string with a summary header block."""
    output = io.StringIO()

    output.write(f"# total={summary.total} valid={summary.valid_count} "
                 f"invalid={summary.invalid_count} conflicts={summary.conflict_count}\n")

    writer = csv.writer(output)
    writer.writerow(["expression_a", "expression_b", "reason"])
    for c in conflicts:
        writer.writerow([c.expression_a, c.expression_b, c.reason])

    return output.getvalue()


def export(fmt: str, summary: CrontabSummary, conflicts: List[Conflict]) -> str:
    """Dispatch export by format name.

    Args:
        fmt: Output format; must be one of 'json' or 'csv'.
        summary: Aggregated crontab statistics.
        conflicts: List of detected scheduling conflicts.

    Returns:
        Formatted string representation of the results.

    Raises:
        ValueError: If *fmt* is not a supported format.
    """
    if fmt == "json":
        return export_json(summary, conflicts)
    if fmt == "csv":
        return export_csv(summary, conflicts)
    raise ValueError(
        f"Unsupported export format: {fmt!r}. "
        f"Supported formats are: {', '.join(SUPPORTED_FORMATS)}"
    )

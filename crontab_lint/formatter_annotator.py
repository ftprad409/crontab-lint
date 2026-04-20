"""Format annotated crontab lines for terminal output."""

from typing import List
from .annotator import AnnotatedLine

_OK = "\u2713"
_FAIL = "\u2717"


def format_annotated_line(line: AnnotatedLine) -> str:
    """Format a single annotated line."""
    if line.is_blank:
        return ""
    if line.is_comment:
        return f"  {line.raw.strip()}"

    num = f"{line.line_number:>3}"
    if line.is_valid:
        status = _OK
        detail = f"  # {line.explanation}" if line.explanation else ""
        return f"{num}  [{status}]  {line.expression}{detail}"
    else:
        status = _FAIL
        return f"{num}  [{status}]  {line.expression}\n       ERROR: {line.error}"


def format_annotation_report(lines: List[AnnotatedLine]) -> str:
    """Format the full annotation report."""
    parts = ["=" * 60, "Crontab Annotation Report", "=" * 60]

    for line in lines:
        formatted = format_annotated_line(line)
        if formatted:
            parts.append(formatted)

    total = sum(1 for l in lines if not l.is_comment and not l.is_blank)
    valid = sum(1 for l in lines if not l.is_comment and not l.is_blank and l.is_valid)
    invalid = total - valid

    parts.append("-" * 60)
    parts.append(f"Total: {total}  Valid: {valid}  Invalid: {invalid}")

    return "\n".join(parts)

"""Annotate crontab lines with inline explanations and validation status."""

from dataclasses import dataclass
from typing import List

from .parser import parse, is_valid
from .explainer import explain


@dataclass
class AnnotatedLine:
    line_number: int
    raw: str
    is_comment: bool
    is_blank: bool
    is_valid: bool
    expression: str
    explanation: str
    error: str


def _is_comment(line: str) -> bool:
    return line.strip().startswith("#")


def _is_blank(line: str) -> bool:
    return line.strip() == ""


def annotate(lines: List[str]) -> List[AnnotatedLine]:
    """Annotate each line in a crontab with explanation and validity."""
    annotated = []
    for i, raw in enumerate(lines, start=1):
        comment = _is_comment(raw)
        blank = _is_blank(raw)

        if comment or blank:
            annotated.append(AnnotatedLine(
                line_number=i,
                raw=raw,
                is_comment=comment,
                is_blank=blank,
                is_valid=True,
                expression=raw.strip(),
                explanation="",
                error="",
            ))
            continue

        expr_str = raw.strip()
        valid = is_valid(expr_str)
        explanation = ""
        error = ""

        if valid:
            try:
                expr = parse(expr_str)
                explanation = explain(expr)
            except Exception as e:  # pragma: no cover
                explanation = ""
                error = str(e)
        else:
            error = f"Invalid cron expression: '{expr_str}'"

        annotated.append(AnnotatedLine(
            line_number=i,
            raw=raw,
            is_comment=comment,
            is_blank=blank,
            is_valid=valid,
            expression=expr_str,
            explanation=explanation,
            error=error,
        ))

    return annotated

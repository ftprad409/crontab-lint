"""Generates a per-line validation report for a crontab file or list of expressions."""

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import parse, is_valid
from .explainer import explain
from .normalizer import normalize


@dataclass
class ValidationEntry:
    line_number: int
    raw: str
    normalized: Optional[str]
    valid: bool
    explanation: Optional[str]
    error: Optional[str]
    is_comment: bool
    is_blank: bool


@dataclass
class ValidationReport:
    entries: List[ValidationEntry] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.entries)

    @property
    def valid_count(self) -> int:
        return sum(1 for e in self.entries if e.valid)

    @property
    def invalid_count(self) -> int:
        return sum(1 for e in self.entries if not e.valid and not e.is_comment and not e.is_blank)

    @property
    def skipped_count(self) -> int:
        return sum(1 for e in self.entries if e.is_comment or e.is_blank)


def _is_comment(line: str) -> bool:
    return line.strip().startswith("#")


def _is_blank(line: str) -> bool:
    return line.strip() == ""


def build_report(lines: List[str]) -> ValidationReport:
    """Build a ValidationReport from a list of raw crontab lines."""
    report = ValidationReport()

    for i, raw in enumerate(lines, start=1):
        comment = _is_comment(raw)
        blank = _is_blank(raw)

        if comment or blank:
            report.entries.append(ValidationEntry(
                line_number=i,
                raw=raw,
                normalized=None,
                valid=False,
                explanation=None,
                error=None,
                is_comment=comment,
                is_blank=blank,
            ))
            continue

        normed = normalize(raw.strip())
        valid = is_valid(normed)
        explanation: Optional[str] = None
        error: Optional[str] = None

        if valid:
            expr = parse(normed)
            explanation = explain(expr)
        else:
            error = f"Invalid cron expression: '{normed}'"

        report.entries.append(ValidationEntry(
            line_number=i,
            raw=raw,
            normalized=normed,
            valid=valid,
            explanation=explanation,
            error=error,
            is_comment=False,
            is_blank=False,
        ))

    return report

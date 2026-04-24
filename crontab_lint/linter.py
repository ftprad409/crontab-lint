"""High-level linting pipeline that combines parsing, conflict detection,
scheduling, and annotation into a single unified lint result."""

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import parse, is_valid
from .explainer import explain
from .conflict_detector import detect_conflicts, Conflict
from .annotator import annotate, AnnotatedLine
from .normalizer import normalize
from .scheduler import next_run
from .validator_report import build_report, ValidationReport

import datetime


@dataclass
class LintIssue:
    """Represents a single linting issue found in a crontab expression."""

    line_number: int
    expression: str
    severity: str          # "error" | "warning" | "info"
    message: str
    suggestion: Optional[str] = None


@dataclass
class LintResult:
    """Aggregated result of linting a crontab file or set of expressions."""

    issues: List[LintIssue] = field(default_factory=list)
    conflicts: List[Conflict] = field(default_factory=list)
    validation_report: Optional[ValidationReport] = None
    annotated_lines: List[AnnotatedLine] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == "warning" for i in self.issues)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")

    @property
    def is_clean(self) -> bool:
        """True when there are no errors, warnings, or conflicts."""
        return not self.issues and not self.conflicts


def _check_expression(line_number: int, raw: str) -> List[LintIssue]:
    """Validate and inspect a single crontab expression, returning any issues."""
    issues: List[LintIssue] = []

    normalized = normalize(raw)
    expr = parse(normalized)

    if not is_valid(expr):
        issues.append(
            LintIssue(
                line_number=line_number,
                expression=raw,
                severity="error",
                message=f"Invalid crontab expression: '{raw}'",
                suggestion="Check field ranges: min(0-59) hour(0-23) dom(1-31) month(1-12) dow(0-7)",
            )
        )
        return issues

    # Warn about expressions that run every minute (potentially noisy).
    if normalized == "* * * * *":
        issues.append(
            LintIssue(
                line_number=line_number,
                expression=raw,
                severity="warning",
                message="Expression runs every minute — verify this is intentional.",
                suggestion="Consider a less frequent schedule, e.g. '*/5 * * * *'.",
            )
        )

    # Warn about day-of-month 31 combined with months that have fewer days.
    fields = normalized.split()
    if len(fields) == 5:
        dom, month = fields[2], fields[3]
        short_months = {"2", "4", "6", "9", "11"}
        if dom == "31" and month in short_months:
            issues.append(
                LintIssue(
                    line_number=line_number,
                    expression=raw,
                    severity="warning",
                    message=(
                        f"Day-of-month 31 will never trigger in month {month} "
                        "(which has fewer than 31 days)."
                    ),
                    suggestion="Use 'L' semantics or adjust the month field.",
                )
            )

    return issues


def lint(lines: List[str], reference_dt: Optional[datetime.datetime] = None) -> LintResult:
    """Lint a list of raw crontab lines.

    Args:
        lines: Raw lines from a crontab file, including comments and blanks.
        reference_dt: Reference datetime for next-run calculations (defaults to now).

    Returns:
        A :class:`LintResult` containing all issues, conflicts, and annotations.
    """
    if reference_dt is None:
        reference_dt = datetime.datetime.now()

    all_issues: List[LintIssue] = []
    expressions: List[str] = []

    for lineno, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        issues = _check_expression(lineno, stripped)
        all_issues.extend(issues)
        if not any(i.severity == "error" for i in issues):
            expressions.append(normalize(stripped))

    conflicts = detect_conflicts(expressions)
    annotated = annotate(lines)
    report = build_report(lines)

    return LintResult(
        issues=all_issues,
        conflicts=conflicts,
        validation_report=report,
        annotated_lines=annotated,
    )

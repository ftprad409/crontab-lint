"""Tag crontab expressions with human-readable schedule categories and metadata."""

from dataclasses import dataclass, field
from typing import List, Optional
from crontab_lint.parser import parse, is_valid
from crontab_lint.grouper import _classify


@dataclass
class TaggedExpression:
    raw: str
    expression: Optional[str]
    tags: List[str]
    valid: bool
    comment: Optional[str] = None


def _is_comment(line: str) -> bool:
    return line.strip().startswith("#")


def _is_blank(line: str) -> bool:
    return line.strip() == ""


def _extract_inline_comment(expression: str):
    """Split expression from trailing inline comment."""
    if "#" in expression:
        idx = expression.index("#")
        return expression[:idx].strip(), expression[idx + 1:].strip()
    return expression.strip(), None


def _build_tags(expr_str: str) -> List[str]:
    tags = []
    if not is_valid(expr_str):
        tags.append("invalid")
        return tags

    classification = _classify(expr_str)
    tags.append(classification.lower().replace(" ", "-"))

    parsed = parse(expr_str)
    if parsed and parsed.minute == "*/5":
        tags.append("frequent")
    elif parsed and parsed.minute == "*/15":
        tags.append("quarter-hourly")
    elif parsed and parsed.minute == "*/30":
        tags.append("half-hourly")

    if parsed and parsed.day_of_week in ("1-5", "MON-FRI"):
        tags.append("weekdays-only")
    if parsed and parsed.day_of_week in ("6,0", "0,6", "SAT,SUN", "SUN,SAT"):
        tags.append("weekends-only")

    return tags


def tag(lines: List[str]) -> List[TaggedExpression]:
    """Tag each non-blank, non-comment line with schedule metadata."""
    results = []
    for line in lines:
        stripped = line.strip()
        if _is_blank(stripped) or _is_comment(stripped):
            continue
        expr_str, comment = _extract_inline_comment(stripped)
        valid = is_valid(expr_str)
        tags = _build_tags(expr_str)
        results.append(TaggedExpression(
            raw=stripped,
            expression=expr_str,
            tags=tags,
            valid=valid,
            comment=comment,
        ))
    return results

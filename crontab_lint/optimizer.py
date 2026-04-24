"""Optimizer: suggests simplified equivalents for verbose cron expressions."""

from dataclasses import dataclass, field
from typing import Optional
from crontab_lint.parser import is_valid


@dataclass
class OptimizationSuggestion:
    original: str
    suggested: str
    reason: str


@dataclass
class OptimizationResult:
    expression: str
    suggestions: list[OptimizationSuggestion] = field(default_factory=list)

    @property
    def has_suggestions(self) -> bool:
        return len(self.suggestions) > 0


_SHORTHAND_MAP = {
    ("0", "0", "1", "1", "*"): "@yearly",
    ("0", "0", "1", "*", "*"): "@monthly",
    ("0", "0", "*", "*", "0"): "@weekly",
    ("0", "0", "*", "*", "*"): "@daily",
    ("0", "*", "*", "*", "*"): "@hourly",
    ("*", "*", "*", "*", "*"): "@reboot",
}


def _parts(expression: str) -> Optional[tuple[str, ...]]:
    parts = expression.strip().split()
    if len(parts) == 5:
        return tuple(parts)
    return None


def _check_shorthand(parts: tuple[str, ...]) -> Optional[OptimizationSuggestion]:
    shorthand = _SHORTHAND_MAP.get(parts)
    if shorthand:
        return OptimizationSuggestion(
            original=" ".join(parts),
            suggested=shorthand,
            reason=f"Use {shorthand} shorthand instead of explicit fields",
        )
    return None


def _check_redundant_step(parts: tuple[str, ...]) -> list[OptimizationSuggestion]:
    suggestions = []
    labels = ["minute", "hour", "day-of-month", "day-of-week", "month"]
    ranges = {"minute": 60, "hour": 24, "day-of-month": 31, "day-of-week": 7, "month": 12}
    for i, part in enumerate(parts):
        label = labels[i]
        if part.startswith("*/"):
            try:
                step = int(part[2:])
                max_val = ranges[label]
                if step == 1:
                    suggestions.append(OptimizationSuggestion(
                        original=part,
                        suggested="*",
                        reason=f"{label}: '*/1' is equivalent to '*'",
                    ))
                elif max_val % step == 0 and step >= max_val:
                    suggestions.append(OptimizationSuggestion(
                        original=part,
                        suggested="*",
                        reason=f"{label}: step equals or exceeds range, simplify to '*'",
                    ))
            except ValueError:
                pass
    return suggestions


def optimize(expression: str) -> OptimizationResult:
    """Analyse a cron expression and return optimization suggestions."""
    result = OptimizationResult(expression=expression)
    if not is_valid(expression):
        return result

    parts = _parts(expression)
    if parts is None:
        return result

    shorthand = _check_shorthand(parts)
    if shorthand:
        result.suggestions.append(shorthand)

    result.suggestions.extend(_check_redundant_step(parts))
    return result

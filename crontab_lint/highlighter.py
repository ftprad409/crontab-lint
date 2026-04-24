"""Syntax highlighter for crontab expressions.

Produces ANSI-coloured representations of cron fields so that each
field (minute, hour, dom, month, dow) stands out when printed to a
terminal.  Non-expression lines (comments, blanks) are rendered with
neutral styling.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from crontab_lint.parser import is_valid

# ANSI escape helpers
_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"

_FIELD_COLOURS = [
    "\033[36m",  # minute  – cyan
    "\033[32m",  # hour    – green
    "\033[33m",  # dom     – yellow
    "\033[35m",  # month   – magenta
    "\033[34m",  # dow     – blue
]
_COMMENT_COLOUR = "\033[90m"  # dark grey
_ERROR_COLOUR = "\033[31m"    # red


@dataclass
class HighlightedLine:
    raw: str
    rendered: str
    is_expression: bool
    is_valid: bool


def highlight_expression(expression: str) -> str:
    """Return an ANSI-coloured version of *expression*.

    If the expression is invalid the whole string is rendered in red.
    If it is valid each of the five cron fields gets its own colour and
    the command portion (everything after the fifth field) is bold.
    """
    parts = expression.split(None, 5)
    if len(parts) < 5 or not is_valid(expression):
        return f"{_ERROR_COLOUR}{expression}{_RESET}"

    coloured_fields = [
        f"{_FIELD_COLOURS[i]}{parts[i]}{_RESET}"
        for i in range(5)
    ]
    command = f"{_BOLD}{parts[5]}{_RESET}" if len(parts) == 6 else ""
    tokens = coloured_fields + ([command] if command else [])
    return " ".join(tokens)


def highlight(lines: List[str]) -> List[HighlightedLine]:
    """Highlight a list of raw crontab lines.

    Comments and blank lines are dimmed; valid expressions are
    field-coloured; invalid expressions are shown in red.
    """
    result: List[HighlightedLine] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            result.append(HighlightedLine(line, "", False, False))
            continue
        if stripped.startswith("#"):
            rendered = f"{_COMMENT_COLOUR}{_DIM}{line}{_RESET}"
            result.append(HighlightedLine(line, rendered, False, False))
            continue
        valid = is_valid(stripped)
        rendered = highlight_expression(stripped)
        result.append(HighlightedLine(line, rendered, True, valid))
    return result

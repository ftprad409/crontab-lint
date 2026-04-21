"""Normalizer for crontab expressions — expands aliases and shorthand notations."""

from typing import Optional

# Standard cron aliases mapped to their 5-field equivalents
_ALIASES: dict[str, str] = {
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly": "0 0 1 * *",
    "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
}

# Named month replacements (case-insensitive)
_MONTHS: dict[str, str] = {
    "jan": "1", "feb": "2", "mar": "3", "apr": "4",
    "may": "5", "jun": "6", "jul": "7", "aug": "8",
    "sep": "9", "oct": "10", "nov": "11", "dec": "12",
}

# Named weekday replacements (case-insensitive)
_WEEKDAYS: dict[str, str] = {
    "sun": "0", "mon": "1", "tue": "2", "wed": "3",
    "thu": "4", "fri": "5", "sat": "6",
}


def _replace_names(field: str, mapping: dict[str, str]) -> str:
    """Replace named tokens in a field using the provided mapping."""
    result = field
    for name, value in mapping.items():
        result = result.lower().replace(name, value)
    return result


def normalize(expression: str) -> Optional[str]:
    """Normalize a crontab expression.

    - Expands @aliases to 5-field expressions.
    - Replaces named months and weekdays with numeric equivalents.
    - Strips extra whitespace.

    Returns the normalized expression string, or None if input is blank/comment.
    """
    stripped = expression.strip()

    if not stripped or stripped.startswith("#"):
        return None

    # Check for alias
    lower = stripped.lower()
    if lower in _ALIASES:
        return _ALIASES[lower]

    parts = stripped.split()
    if len(parts) != 5:
        # Return as-is for validation to catch the error
        return stripped

    minute, hour, dom, month, dow = parts

    month = _replace_names(month, _MONTHS)
    dow = _replace_names(dow, _WEEKDAYS)

    return f"{minute} {hour} {dom} {month} {dow}"

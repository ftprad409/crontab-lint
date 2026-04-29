"""Formatters for AliasResult output."""

from __future__ import annotations

from crontab_lint.aliaser import AliasEntry, AliasResult

_CHECK = "\u2713"
_CROSS = "\u2717"


def format_alias_entry(entry: AliasEntry) -> str:
    """Format a single alias entry as a human-readable line."""
    status = _CHECK if entry.valid else _CROSS
    parts = [f"[{status}] {entry.alias!r:20s} -> {entry.expression}"] 
    if entry.comment:
        parts.append(f"  # {entry.comment}")
    return "".join(parts)


def format_alias_result(result: AliasResult) -> str:
    """Format the full alias result as a report string."""
    lines: list[str] = []
    lines.append("=== Cron Aliases ===")
    lines.append("")

    if result.entries:
        lines.append("Aliases:")
        for entry in result.entries:
            lines.append(f"  {format_alias_entry(entry)}")
    else:
        lines.append("  (no aliases registered)")

    lines.append("")
    lines.append(f"Total : {result.total_aliases}")

    if result.skipped:
        lines.append("")
        lines.append("Skipped (invalid or duplicate):")
        for name in result.skipped:
            lines.append(f"  - {name}")

    return "\n".join(lines)


def format_alias_lookup(alias_name: str, result: AliasResult) -> str:
    """Format a single alias lookup result."""
    entry = result.resolve(alias_name)
    if entry is None:
        return f"Alias {alias_name!r} not found."
    return format_alias_entry(entry)

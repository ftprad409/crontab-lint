"""Formatters for pinned crontab expressions."""

from __future__ import annotations

from crontab_lint.pinner import PinnedExpression, PinResult

_DATE_FMT = "%Y-%m-%d %H:%M UTC"


def format_pinned_entry(entry: PinnedExpression) -> str:
    """Format a single pinned expression for display."""
    timestamp = entry.pinned_at.strftime(_DATE_FMT)
    lines = [
        f"  ✔ {entry.expression}",
        f"    Reason  : {entry.reason}",
        f"    Pinned by: {entry.pinned_by} on {timestamp}",
    ]
    return "\n".join(lines)


def format_pin_result(result: PinResult) -> str:
    """Format the full result of a pin operation."""
    sections: list[str] = ["=== Pin Result ==="]

    if result.pinned:
        sections.append(f"Pinned ({result.total_pinned}):")
        for entry in result.pinned:
            sections.append(format_pinned_entry(entry))
    else:
        sections.append("No expressions were pinned.")

    if result.skipped_invalid:
        sections.append(f"\nSkipped — invalid ({len(result.skipped_invalid)}):")
        for expr in result.skipped_invalid:
            sections.append(f"  ✗ {expr}")

    if result.skipped_already_pinned:
        sections.append(
            f"\nSkipped — already pinned ({len(result.skipped_already_pinned)}):"
        )
        for expr in result.skipped_already_pinned:
            sections.append(f"  ~ {expr}")

    return "\n".join(sections)


def format_pinned_list(pinned: list[PinnedExpression]) -> str:
    """Format a list of all currently pinned expressions."""
    if not pinned:
        return "No expressions are currently pinned."

    header = f"=== Pinned Expressions ({len(pinned)}) ==="
    entries = [format_pinned_entry(e) for e in pinned]
    return "\n".join([header] + entries)

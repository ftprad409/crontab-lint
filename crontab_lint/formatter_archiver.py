"""Format archive results for CLI output."""

from __future__ import annotations

from crontab_lint.archiver import ArchiveResult, ArchivedEntry

_CHECK = "\u2713"
_CROSS = "\u2717"


def format_archived_entry(entry: ArchivedEntry) -> str:
    """Format a single archived entry as a human-readable line."""
    status = _CHECK if entry.valid else _CROSS
    label_part = f"  [{entry.label}]" if entry.label else ""
    return f"  {status} {entry.expression}{label_part}  (archived: {entry.archived_at})"


def format_archive_result(result: ArchiveResult) -> str:
    """Format the full archive result as a report string."""
    lines: list[str] = []

    header = "Archive Report"
    if result.source:
        header += f" — {result.source}"
    lines.append(header)
    lines.append("-" * len(header))

    if not result.entries:
        lines.append("  (no expressions archived)")
    else:
        for entry in result.entries:
            lines.append(format_archived_entry(entry))

    lines.append("")
    lines.append(
        f"Total: {result.total}  "
        f"Valid: {result.valid_count}  "
        f"Invalid: {result.invalid_count}"
    )
    return "\n".join(lines)


def format_archive_summary(result: ArchiveResult) -> str:
    """Return a compact one-line summary of an archive result."""
    src = f" ({result.source})" if result.source else ""
    return (
        f"Archived{src}: {result.total} entries, "
        f"{result.valid_count} valid, {result.invalid_count} invalid."
    )

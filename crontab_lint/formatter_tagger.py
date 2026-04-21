"""Format tagged crontab expressions for CLI output."""

from typing import List
from crontab_lint.tagger import TaggedExpression


def format_tagged_line(entry: TaggedExpression) -> str:
    """Format a single tagged expression as a readable line."""
    status = "✔" if entry.valid else "✘"
    tag_str = ", ".join(entry.tags) if entry.tags else "(none)"
    comment_str = f"  # {entry.comment}" if entry.comment else ""
    return f"  {status} {entry.expression}{comment_str}\n     Tags: [{tag_str}]"


def format_tag_report(entries: List[TaggedExpression]) -> str:
    """Format a full tag report for a list of tagged expressions."""
    if not entries:
        return "No expressions to tag."

    lines = ["=" * 50, "Crontab Tag Report", "=" * 50]
    for entry in entries:
        lines.append(format_tagged_line(entry))
        lines.append("")

    tag_index: dict = {}
    for entry in entries:
        for t in entry.tags:
            tag_index.setdefault(t, []).append(entry.expression)

    lines.append("-" * 50)
    lines.append("Tag Index:")
    for tag, exprs in sorted(tag_index.items()):
        lines.append(f"  [{tag}]: {len(exprs)} expression(s)")

    return "\n".join(lines)

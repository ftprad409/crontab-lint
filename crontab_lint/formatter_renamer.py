"""Format RenameResult objects for human-readable CLI output."""

from __future__ import annotations

from typing import List

from crontab_lint.renamer import RenameResult, total_replaced


def format_rename_result(result: RenameResult) -> str:
    """Return a concise summary of a rename operation."""
    lines: List[str] = ["=== Rename Report ==="]

    if result.skipped_invalid_source:
        for expr in result.skipped_invalid_source:
            lines.append(f"  [ERROR] Source expression is invalid: {expr!r}")
        return "\n".join(lines)

    if result.skipped_invalid_target:
        for expr in result.skipped_invalid_target:
            lines.append(f"  [ERROR] Target expression is invalid: {expr!r}")
        return "\n".join(lines)

    replaced = total_replaced(result)
    lines.append(f"  Replacements made : {replaced}")

    if replaced == 0:
        lines.append("  No matching expressions found.")
    else:
        lines.append("  Changes:")
        for lineno, old, new in result.replacements:
            lines.append(f"    line {lineno:>4}: {old}  ->  {new}")

    return "\n".join(lines)


def format_rename_diff(result: RenameResult) -> str:
    """Return a unified-diff-style view of the renamed lines."""
    if not result.replacements:
        return "(no changes)"

    replaced_linenos = {r[0] for r in result.replacements}
    diff_lines: List[str] = []

    for lineno, line in enumerate(result.lines, start=1):
        if lineno in replaced_linenos:
            # Find the original expression for this line
            match = next(r for r in result.replacements if r[0] == lineno)
            diff_lines.append(f"- line {lineno:>4}: {match[1]}")
            diff_lines.append(f"+ line {lineno:>4}: {match[2]}")
        else:
            diff_lines.append(f"  line {lineno:>4}: {line}")

    return "\n".join(diff_lines)

"""Formatter for optimizer results."""

from crontab_lint.optimizer import OptimizationResult


def format_optimization_result(result: OptimizationResult) -> str:
    lines = [f"Expression : {result.expression}"]
    if not result.has_suggestions:
        lines.append("  ✔ No optimizations suggested.")
        return "\n".join(lines)

    lines.append(f"  {len(result.suggestions)} suggestion(s):")
    for s in result.suggestions:
        lines.append(f"    ➤ {s.original!r} → {s.suggested!r}")
        lines.append(f"      Reason: {s.reason}")
    return "\n".join(lines)


def format_optimization_report(results: list[OptimizationResult]) -> str:
    if not results:
        return "No expressions to optimize."

    sections = ["=== Optimization Report ==="]
    total_suggestions = sum(len(r.suggestions) for r in results)

    for result in results:
        sections.append(format_optimization_result(result))

    sections.append("")
    sections.append(f"Total expressions : {len(results)}")
    sections.append(
        f"Expressions with suggestions : {sum(1 for r in results if r.has_suggestions)}"
    )
    sections.append(f"Total suggestions : {total_suggestions}")
    return "\n".join(sections)

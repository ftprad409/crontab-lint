"""CLI entry point for crontab-lint."""

import argparse
import sys
from .parser import is_valid, parse
from .explainer import explain
from .conflict_detector import detect_conflicts
from .formatter import format_lint_report


def _read_expressions(args) -> list:
    if args.file:
        with open(args.file) as fh:
            lines = [l.strip() for l in fh if l.strip() and not l.startswith("#")]
        return lines
    return args.expressions or []


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="crontab-lint",
        description="Validate and explain crontab expressions with conflict detection.",
    )
    parser.add_argument("expressions", nargs="*", help="Cron expressions to lint")
    parser.add_argument("-f", "--file", help="File containing one cron expression per line")
    parser.add_argument("--no-explain", action="store_true", help="Skip human-readable explanations")
    args = parser.parse_args(argv)

    expressions = _read_expressions(args)
    if not expressions:
        parser.print_help()
        sys.exit(0)

    results = []
    for expr in expressions:
        valid = is_valid(expr)
        explanation = ""
        if valid and not args.no_explain:
            try:
                explanation = explain(parse(expr))
            except Exception:
                explanation = ""
        results.append({"expression": expr, "valid": valid, "explanation": explanation})

    conflicts = detect_conflicts(expressions)
    report = format_lint_report(results, conflicts)
    print(report)

    any_invalid = any(not r["valid"] for r in results)
    sys.exit(1 if any_invalid else 0)


if __name__ == "__main__":
    main()

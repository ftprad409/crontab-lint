"""CLI entry point for crontab-lint."""
import argparse
import sys
from typing import List

from .parser import is_valid, parse
from .explainer import explain
from .conflict_detector import detect_conflicts
from .summarizer import summarize
from .formatter import format_lint_report, format_summary


def _read_expressions(path: str) -> List[str]:
    with open(path) as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="crontab-lint",
        description="Validate and explain crontab expressions.",
    )
    parser.add_argument("file", nargs="?", help="Path to crontab file")
    parser.add_argument("--expr", help="Single crontab expression to lint")
    parser.add_argument("--summary", action="store_true", help="Print summary statistics")
    args = parser.parse_args(argv)

    if args.expr:
        expressions = [args.expr]
    elif args.file:
        expressions = _read_expressions(args.file)
    else:
        parser.print_help()
        sys.exit(1)

    results = []
    valid_parsed = []
    for expr in expressions:
        valid = is_valid(expr)
        explanation = explain(expr) if valid else "Expression is invalid."
        results.append((expr, valid, explanation))
        if valid:
            valid_parsed.append(parse(expr))

    conflicts = detect_conflicts(valid_parsed)
    report = format_lint_report(expressions, results, conflicts)
    print(report, end="")

    if args.summary:
        summary = summarize(expressions)
        print(format_summary(summary), end="")

    has_errors = any(not v for _, v, _ in results) or conflicts
    sys.exit(1 if has_errors else 0)


if __name__ == "__main__":
    main()

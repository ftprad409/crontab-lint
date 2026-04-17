"""Human-readable explanations for crontab expressions."""

from crontab_lint.parser import CronExpression


def _explain_field(name: str, raw: str) -> str:
    labels = {
        "minute": "minute",
        "hour": "hour",
        "day_of_month": "day of month",
        "month": "month",
        "day_of_week": "day of week",
    }
    MONTHS = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    DAYS = [" "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    labelname]

    if raw == "*":
        return f"every {label}"

    if raw.startswith("*/"):
        n        return f"every {step} {label}(s)"

    if "-" in raw:
        a, b = raw.split("-")
        if name == "month":
            return f"{label} from {MONTHS[int(a)]} to {MONTHS[int(b)]}"
        if name == "day_of_week":
            return f"{label} from {DAYS[int(a)]} to {DAYS[int(b)]}"
        return f"{label} from {a} to {b}"

    if "," in raw:
        values = raw.split(",")
        if name == "month":
            values = [MONTHS[int(v)] for v in values]
        elif name == "day_of_week":
            values = [DAYS[int(v)] for v in values]
        return f"{label} in [{', '.join(values)}]"

    if name == "month":
        return f"{label} {MONTHS[int(raw)]}"
    if name == "day_of_week":
        return f"{label} {DAYS[int(raw)]}"

    return f"{label} {raw}"


def explain(expr: CronExpression) -> str:
    """Return a human-readable explanation of a parsed cron expression."""
    if not expr.is_valid:
        return "Invalid expression: " + "; ".join(expr.errors)

    parts = [_explain_field(f.name, f.raw) for f in expr.fields]
    return "Runs at: " + ", ".join(parts) + "."

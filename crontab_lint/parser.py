"""Crontab expression parser and validator."""

from dataclasses import dataclass
from typing import Optional

FIELD_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day_of_month": (1, 31),
    "month": (1, 12),
    "day_of_week": (0, 7),
}

FIELD_NAMES = list(FIELD_RANGES.keys())


@dataclass
class CronField:
    name: str
    raw: str
    min_val: int
    max_val: int

    def validate(self) -> Optional[str]:
        """Return error message if invalid, else None."""
        val = self.raw
        lo, hi = self.min_val, self.max_val

        if val == "*":
            return None

        if val.startswith("*/"):
            step = val[2:]
            if not step.isdigit() or int(step) < 1:
                return f"{self.name}: invalid step '{val}'"
            return None

        if "-" in val:
            parts = val.split("-")
            if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
                return f"{self.name}: invalid range '{val}'"
            a, b = int(parts[0]), int(parts[1])
            if not (lo <= a <= hi) or not (lo <= b <= hi) or a > b:
                return f"{self.name}: range '{val}' out of bounds [{lo}-{hi}]"
            return None

        if "," in val:
            for item in val.split(","):
                if not item.isdigit() or not (lo <= int(item) <= hi):
                    return f"{self.name}: invalid list value '{item}' in '{val}'"
            return None

        if val.isdigit():
            if not (lo <= int(val) <= hi):
                return f"{self.name}: value '{val}' out of bounds [{lo}-{hi}]"
            return None

        return f"{self.name}: unrecognized expression '{val}'"


@dataclass
class CronExpression:
    raw: str
    fields: list
    errors: list

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0


def parse(expression: str) -> CronExpression:
    """Parse and validate a crontab expression string."""
    parts = expression.strip().split()
    errors = []

    if len(parts) != 5:
        return CronExpression(
            raw=expression,
            fields=[],
            errors=[f"Expected 5 fields, got {len(parts)}"],
        )

    fields = [
        CronField(name=FIELD_NAMES[i], raw=parts[i], min_val=r[0], max_val=r[1])
        for i, (name, r) in enumerate(FIELD_RANGES.items())
    ]

    for field in fields:
        err = field.validate()
        if err:
            errors.append(err)

    return CronExpression(raw=expression, fields=fields, errors=errors)

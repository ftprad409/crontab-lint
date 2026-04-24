"""Template library for common crontab patterns."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class CronTemplate:
    name: str
    expression: str
    description: str
    tags: List[str] = field(default_factory=list)


_TEMPLATES: Dict[str, CronTemplate] = {
    "every_minute": CronTemplate(
        name="every_minute",
        expression="* * * * *",
        description="Run every minute",
        tags=["frequent", "realtime"],
    ),
    "every_hour": CronTemplate(
        name="every_hour",
        expression="0 * * * *",
        description="Run at the start of every hour",
        tags=["hourly"],
    ),
    "daily_midnight": CronTemplate(
        name="daily_midnight",
        expression="0 0 * * *",
        description="Run once a day at midnight",
        tags=["daily", "maintenance"],
    ),
    "daily_noon": CronTemplate(
        name="daily_noon",
        expression="0 12 * * *",
        description="Run once a day at noon",
        tags=["daily"],
    ),
    "weekly_sunday": CronTemplate(
        name="weekly_sunday",
        expression="0 0 * * 0",
        description="Run every Sunday at midnight",
        tags=["weekly", "maintenance"],
    ),
    "monthly_first": CronTemplate(
        name="monthly_first",
        expression="0 0 1 * *",
        description="Run on the first day of every month",
        tags=["monthly", "maintenance"],
    ),
    "weekdays_9am": CronTemplate(
        name="weekdays_9am",
        expression="0 9 * * 1-5",
        description="Run at 9 AM on weekdays (Mon-Fri)",
        tags=["weekday", "business-hours"],
    ),
    "every_5_minutes": CronTemplate(
        name="every_5_minutes",
        expression="*/5 * * * *",
        description="Run every 5 minutes",
        tags=["frequent"],
    ),
    "every_15_minutes": CronTemplate(
        name="every_15_minutes",
        expression="*/15 * * * *",
        description="Run every 15 minutes",
        tags=["frequent"],
    ),
    "twice_daily": CronTemplate(
        name="twice_daily",
        expression="0 0,12 * * *",
        description="Run at midnight and noon every day",
        tags=["daily"],
    ),
}


def list_templates() -> List[CronTemplate]:
    """Return all available templates sorted by name."""
    return sorted(_TEMPLATES.values(), key=lambda t: t.name)


def get_template(name: str) -> Optional[CronTemplate]:
    """Return a template by name, or None if not found."""
    return _TEMPLATES.get(name)


def search_templates(query: str) -> List[CronTemplate]:
    """Return templates whose name, description, or tags contain the query."""
    q = query.lower()
    return [
        t for t in list_templates()
        if q in t.name.lower()
        or q in t.description.lower()
        or any(q in tag for tag in t.tags)
    ]

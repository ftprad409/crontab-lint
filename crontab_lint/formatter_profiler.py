"""Formatter for crontab load profiles."""

from .profiler import CrontabProfile


_BAR_WIDTH = 20


def _bar(value: int, max_value: int) -> str:
    if max_value == 0:
        return ""
    filled = round((value / max_value) * _BAR_WIDTH)
    return "#" * filled + "-" * (_BAR_WIDTH - filled)


def format_hourly_chart(profile: CrontabProfile) -> str:
    """Return an ASCII bar chart of jobs per hour."""
    max_val = max(profile.hourly_load.values(), default=1) or 1
    lines = ["Hourly load distribution:", ""]
    for hour in range(24):
        count = profile.hourly_load[hour]
        bar = _bar(count, max_val)
        marker = " <-- busiest" if hour == profile.busiest_hour else ""
        lines.append(f"  {hour:02d}:00  [{bar}] {count:>3}{marker}")
    return "\n".join(lines)


def format_minutely_chart(profile: CrontabProfile) -> str:
    """Return a compact summary of the top 5 busiest minutes."""
    ranked = sorted(profile.minutely_load.items(), key=lambda x: x[1], reverse=True)[:5]
    lines = ["Top 5 busiest minutes:", ""]
    for minute, count in ranked:
        lines.append(f"  :{minute:02d}  — {count} job(s)")
    return "\n".join(lines)


def format_profile_report(profile: CrontabProfile) -> str:
    """Return a full profile report."""
    sections = [
        "=== Crontab Load Profile ===",
        f"Expressions analysed : {profile.total_expressions}",
        f"Skipped (invalid)    : {profile.skipped_expressions}",
        f"Busiest hour         : {profile.busiest_hour:02d}:00",
        f"Busiest minute       : :{profile.busiest_minute:02d}",
        "",
        format_hourly_chart(profile),
        "",
        format_minutely_chart(profile),
    ]
    return "\n".join(sections)

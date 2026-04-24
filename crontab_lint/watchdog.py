"""Watch a crontab file for changes and report diffs automatically."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from crontab_lint.differ import diff, CrontabDiff


@dataclass
class WatchEvent:
    """Represents a single file-change event detected by the watchdog."""

    path: str
    previous_hash: str
    current_hash: str
    diff: CrontabDiff
    timestamp: float = field(default_factory=time.time)

    @property
    def changed(self) -> bool:
        return self.previous_hash != self.current_hash


def _file_hash(path: Path) -> str:
    """Return the MD5 hex-digest of *path* contents."""
    return hashlib.md5(path.read_bytes()).hexdigest()


def _read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def watch(
    path: str,
    interval: float = 2.0,
    max_events: Optional[int] = None,
    on_change: Optional[Callable[[WatchEvent], None]] = None,
) -> list[WatchEvent]:
    """Poll *path* every *interval* seconds and emit a :class:`WatchEvent`
    whenever the file content changes.

    Parameters
    ----------
    path:
        Filesystem path to the crontab file to monitor.
    interval:
        Polling interval in seconds (default 2).
    max_events:
        Stop after this many change-events have been detected.  Pass ``None``
        to run indefinitely (useful for production; tests pass a small number).
    on_change:
        Optional callback invoked synchronously for every change event.

    Returns
    -------
    list[WatchEvent]
        All events collected during the watch session.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"crontab file not found: {path}")

    previous_lines: list[str] = _read_lines(p)
    previous_hash: str = _file_hash(p)
    events: list[WatchEvent] = []

    while max_events is None or len(events) < max_events:
        time.sleep(interval)

        if not p.exists():
            break

        current_hash = _file_hash(p)
        if current_hash == previous_hash:
            continue

        current_lines = _read_lines(p)
        cron_diff = diff(previous_lines, current_lines)

        event = WatchEvent(
            path=str(p),
            previous_hash=previous_hash,
            current_hash=current_hash,
            diff=cron_diff,
        )
        events.append(event)

        if on_change is not None:
            on_change(event)

        previous_lines = current_lines
        previous_hash = current_hash

    return events

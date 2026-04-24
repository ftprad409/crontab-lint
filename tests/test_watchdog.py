"""Tests for crontab_lint.watchdog."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from crontab_lint.watchdog import WatchEvent, watch, _file_hash


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

CRON_V1 = "0 * * * * /usr/bin/backup\n*/5 * * * * /usr/bin/cleanup\n"
CRON_V2 = "0 * * * * /usr/bin/backup\n0 2 * * * /usr/bin/report\n"


def _write(p: Path, content: str) -> None:
    p.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# WatchEvent unit tests
# ---------------------------------------------------------------------------


def test_watch_event_changed_when_hashes_differ():
    event = WatchEvent(
        path="/etc/crontab",
        previous_hash="aaa",
        current_hash="bbb",
        diff=None,  # type: ignore[arg-type]
    )
    assert event.changed is True


def test_watch_event_not_changed_when_hashes_equal():
    event = WatchEvent(
        path="/etc/crontab",
        previous_hash="abc",
        current_hash="abc",
        diff=None,  # type: ignore[arg-type]
    )
    assert event.changed is False


def test_watch_event_has_timestamp():
    before = time.time()
    event = WatchEvent(path="x", previous_hash="a", current_hash="b", diff=None)  # type: ignore[arg-type]
    after = time.time()
    assert before <= event.timestamp <= after


# ---------------------------------------------------------------------------
# _file_hash
# ---------------------------------------------------------------------------


def test_file_hash_consistent(tmp_path):
    p = tmp_path / "crontab"
    _write(p, CRON_V1)
    assert _file_hash(p) == _file_hash(p)


def test_file_hash_differs_after_write(tmp_path):
    p = tmp_path / "crontab"
    _write(p, CRON_V1)
    h1 = _file_hash(p)
    _write(p, CRON_V2)
    h2 = _file_hash(p)
    assert h1 != h2


# ---------------------------------------------------------------------------
# watch() integration tests (fast, using max_events)
# ---------------------------------------------------------------------------


def test_watch_raises_for_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        watch(str(tmp_path / "nonexistent.crontab"), interval=0.05, max_events=1)


def test_watch_detects_single_change(tmp_path):
    p = tmp_path / "crontab"
    _write(p, CRON_V1)

    collected: list = []

    def _mutate_after_delay():
        time.sleep(0.08)
        _write(p, CRON_V2)

    import threading
    t = threading.Thread(target=_mutate_after_delay, daemon=True)
    t.start()

    events = watch(str(p), interval=0.05, max_events=1)
    t.join(timeout=2)

    assert len(events) == 1
    assert events[0].changed


def test_watch_callback_invoked_on_change(tmp_path):
    p = tmp_path / "crontab"
    _write(p, CRON_V1)
    received: list = []

    import threading

    def _mutate():
        time.sleep(0.08)
        _write(p, CRON_V2)

    t = threading.Thread(target=_mutate, daemon=True)
    t.start()

    watch(str(p), interval=0.05, max_events=1, on_change=received.append)
    t.join(timeout=2)

    assert len(received) == 1
    assert isinstance(received[0], WatchEvent)


def test_watch_diff_contains_added_line(tmp_path):
    p = tmp_path / "crontab"
    _write(p, CRON_V1)

    import threading

    def _mutate():
        time.sleep(0.08)
        _write(p, CRON_V2)

    t = threading.Thread(target=_mutate, daemon=True)
    t.start()

    events = watch(str(p), interval=0.05, max_events=1)
    t.join(timeout=2)

    cron_diff = events[0].diff
    assert len(cron_diff.added) > 0 or len(cron_diff.removed) > 0

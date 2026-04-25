"""Archive crontab expressions with timestamps and restore support."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from crontab_lint.parser import is_valid


@dataclass
class ArchivedEntry:
    expression: str
    archived_at: str
    label: Optional[str] = None
    valid: bool = True


@dataclass
class ArchiveResult:
    entries: List[ArchivedEntry] = field(default_factory=list)
    source: str = ""

    @property
    def total(self) -> int:
        return len(self.entries)

    @property
    def valid_count(self) -> int:
        return sum(1 for e in self.entries if e.valid)

    @property
    def invalid_count(self) -> int:
        return self.total - self.valid_count


def _is_comment(line: str) -> bool:
    return line.strip().startswith("#")


def _is_blank(line: str) -> bool:
    return line.strip() == ""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def archive(lines: List[str], source: str = "", label: Optional[str] = None) -> ArchiveResult:
    """Archive a list of crontab lines, recording validity and timestamp."""
    result = ArchiveResult(source=source)
    for line in lines:
        if _is_comment(line) or _is_blank(line):
            continue
        expr = line.strip()
        valid = is_valid(expr)
        entry = ArchivedEntry(
            expression=expr,
            archived_at=_now_iso(),
            label=label,
            valid=valid,
        )
        result.entries.append(entry)
    return result


def save_archive(result: ArchiveResult, path: Path) -> None:
    """Persist an ArchiveResult to a JSON file."""
    data = {
        "source": result.source,
        "entries": [
            {
                "expression": e.expression,
                "archived_at": e.archived_at,
                "label": e.label,
                "valid": e.valid,
            }
            for e in result.entries
        ],
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_archive(path: Path) -> ArchiveResult:
    """Load an ArchiveResult from a JSON file."""
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = [
        ArchivedEntry(
            expression=e["expression"],
            archived_at=e["archived_at"],
            label=e.get("label"),
            valid=e["valid"],
        )
        for e in data.get("entries", [])
    ]
    return ArchiveResult(entries=entries, source=data.get("source", ""))

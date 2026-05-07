"""Auditor: track and report usage history of profiles and chains."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import List, Dict, Any


class AuditorError(Exception):
    pass


class Auditor:
    """Records and retrieves audit log entries for profile/chain resolution events."""

    LOG_FILE = "audit.log"

    def __init__(self, data_dir: str | Path) -> None:
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._log_path = self._data_dir / self.LOG_FILE

    def record(self, event: str, details: Dict[str, Any]) -> None:
        """Append a timestamped audit entry to the log."""
        entry = {
            "timestamp": time.time(),
            "event": event,
            **details,
        }
        with open(self._log_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")

    def read_all(self) -> List[Dict[str, Any]]:
        """Return all audit log entries as a list of dicts."""
        if not self._log_path.exists():
            return []
        entries: List[Dict[str, Any]] = []
        with open(self._log_path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        return entries

    def filter_by_event(self, event: str) -> List[Dict[str, Any]]:
        """Return only entries matching the given event type."""
        return [e for e in self.read_all() if e.get("event") == event]

    def clear(self) -> None:
        """Remove all audit log entries."""
        if self._log_path.exists():
            os.remove(self._log_path)

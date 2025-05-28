"""Simplified history cache implementation.

This module loosely translates parts of ``cachehistory_server.c`` to Python.
It provides minimal in-memory caching functionality for storing history data.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any, Dict, List, Tuple


class HistoryCache:
    """In-memory store for item history.

    This class implements just enough logic for unit testing.  It loosely
    corresponds to the history processing routines inside
    ``cachehistory_server.c`` such as ``dc_add_history`` and
    ``recalculate_triggers``.
    """

    def __init__(self) -> None:
        self._data: Dict[int, List[Tuple[int, Any]]] = defaultdict(list)

    def add(self, itemid: int, value: Any, timestamp: int | None = None) -> None:
        """Store a value for the given item.

        Parameters mirror the structures filled in ``dc_history_set_value`` in
        the original C implementation.
        """
        if timestamp is None:
            timestamp = int(time.time())
        self._data[itemid].append((timestamp, value))

    def get_last(self, itemid: int) -> Any:
        """Return the most recent value for *itemid* or ``None``."""
        if not self._data[itemid]:
            return None
        return self._data[itemid][-1][1]

    def get_history(self, itemid: int) -> List[Tuple[int, Any]]:
        """Return the full history list for *itemid*."""
        return list(self._data[itemid])

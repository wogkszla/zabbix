from __future__ import annotations

"""Minimal history push implementation."""

import queue
import time
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class ItemValue:
    """Single history record."""

    itemid: int
    value: Any
    timestamp: int


class HistoryPush:
    """Collect item values from history.push requests."""

    def __init__(self) -> None:
        self.queue: "queue.Queue[ItemValue]" = queue.Queue()

    def trapper_process_history_push(self, request: Dict[str, Any]) -> None:
        """Parse *request* dictionary and queue item values."""
        data = request.get("data", [])
        now = int(time.time())
        for entry in data:
            try:
                itemid = int(entry["itemid"])
            except (KeyError, ValueError):
                continue
            value = entry.get("value")
            self.queue.put(ItemValue(itemid=itemid, value=value, timestamp=now))

    def flush(self) -> List[ItemValue]:
        """Return all queued values and clear the queue."""
        items: List[ItemValue] = []
        while True:
            try:
                items.append(self.queue.get_nowait())
            except queue.Empty:
                break
        return items

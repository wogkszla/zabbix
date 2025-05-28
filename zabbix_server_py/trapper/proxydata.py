from __future__ import annotations

"""Simple proxy data queue used by :mod:`zabbix_server_py.trapper.server`."""

import queue
from typing import Any, Dict, List


class ProxyDataManager:
    """Collect proxy data packets for later processing."""

    def __init__(self) -> None:
        self.queue: "queue.Queue[Dict[str, Any]]" = queue.Queue()

    def recv_proxy_data(self, data: Dict[str, Any]) -> None:
        """Store *data* in the internal queue."""
        self.queue.put(data)

    def flush(self) -> List[Dict[str, Any]]:
        """Return all queued proxy data and clear the queue."""
        items: List[Dict[str, Any]] = []
        while True:
            try:
                items.append(self.queue.get_nowait())
            except queue.Empty:
                break
        return items

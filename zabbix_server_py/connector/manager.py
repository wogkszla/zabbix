from __future__ import annotations

import queue
import threading
import time
from typing import Any


class ConnectorManager:
    """Simplified connector manager.

    This class is a minimal Python approximation of the
    ``connector_manager_thread()`` function from the C implementation.
    It listens for results from workers and stores them for inspection.
    """

    def __init__(self) -> None:
        self.task_queue: queue.Queue[Any] = queue.Queue()
        self.result_queue: queue.Queue[Any] = queue.Queue()
        self.received_results: list[Any] = []
        self.running = False

    def add_request(self, data: Any) -> None:
        """Send a request to connector workers."""
        self.task_queue.put(data)

    def run(self) -> None:
        """Main manager loop.

        Polls the result queue in a thread similar to
        ``connector_manager_thread()``.
        """
        self.running = True
        while self.running:
            try:
                result = self.result_queue.get(timeout=0.1)
            except queue.Empty:
                continue
            if result == "STOP":
                self.running = False
                continue
            self.received_results.append(result)

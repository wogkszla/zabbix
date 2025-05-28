from __future__ import annotations

import queue
from typing import Any


class ConnectorWorker:
    """Simplified connector worker.

    This class emulates ``zbx_connector_worker_thread()`` from the
    original C code.  It reads requests from the manager queue and
    places the processed results back.
    """

    def __init__(self, manager: "ConnectorManager") -> None:
        self.manager = manager
        self.running = False

    def run(self) -> None:
        """Worker processing loop.

        Continually reads from :pyattr:`manager.task_queue` and writes results
        into :pyattr:`manager.result_queue`.
        """
        self.running = True
        while self.running:
            try:
                task: Any = self.manager.task_queue.get(timeout=0.1)
            except queue.Empty:
                continue
            if task == "STOP":
                self.manager.result_queue.put("STOP")
                self.running = False
                continue
            self.manager.result_queue.put(f"OK:{task}")

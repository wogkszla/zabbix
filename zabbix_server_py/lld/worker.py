"""Simplified LLD worker from ``lld_worker.c``.

Original functions include::
    lld_register_worker
    lld_value_init
    lld_prepare_value
    lld_compare_value
    lld_process_value
    lld_worker_thread
"""

from __future__ import annotations

import queue
from typing import Any

from .lld import parse_rule, discover_items


class LLDWorker:
    """Process rules received from :class:`LLDManager`."""

    def __init__(self, manager: "LLDManager") -> None:
        self.manager = manager
        self.running = False

    def run(self) -> None:
        """Worker loop mimicking ``lld_worker_thread``."""
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
            rule = parse_rule(task)
            items = discover_items(rule)
            self.manager.result_queue.put(items)

"""Simplified LLD manager from ``lld_manager.c``.

Original functions include::
    lld_manager_init
    lld_register_worker
    lld_queue_request
    lld_process_queue
    lld_process_result
    lld_manager_thread
"""

from __future__ import annotations

import queue
import threading
import time
from typing import Any

from .lld import parse_rule, discover_items


class LLDManager:
    """Very small approximation of the C LLD manager."""

    def __init__(self) -> None:
        self.rule_queue: queue.Queue[str] = queue.Queue()
        self.task_queue: queue.Queue[str] = queue.Queue()
        self.result_queue: queue.Queue[Any] = queue.Queue()
        self.results: list[Any] = []
        self.running = False

    def add_rule(self, rule: str) -> None:
        """Queue a raw discovery rule for processing."""
        self.rule_queue.put(rule)

    def stop(self) -> None:
        self.task_queue.put("STOP")

    def run(self) -> None:
        """Dispatch queued rules and collect worker results."""
        self.running = True
        while self.running:
            try:
                rule = self.rule_queue.get_nowait()
                self.task_queue.put(rule)
            except queue.Empty:
                pass
            try:
                res = self.result_queue.get(timeout=0.1)
            except queue.Empty:
                continue
            if res == "STOP":
                self.running = False
                continue
            self.results.append(res)

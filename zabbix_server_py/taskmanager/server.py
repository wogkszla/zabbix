from __future__ import annotations

"""Simplified task manager thread."""

import queue
import threading
from typing import Any

from zabbix_server_py.rtc.server import CMD_PROXY_CONFIG_CACHE_RELOAD

from .proxy_tasks import ProxyTasks


class TaskManagerThread:
    """Very small approximation of ``taskmanager_thread``."""

    def __init__(self, proxy_tasks: ProxyTasks | None = None, interval: float = 0.1) -> None:
        self.proxy_tasks = proxy_tasks or ProxyTasks()
        self.interval = interval
        self._rtc_queue: queue.Queue[tuple[str, Any | None]] = queue.Queue()
        self._stop_event = threading.Event()
        # record processed actions for tests
        self.actions: list[tuple[str, Any | None]] = []

    # public API -------------------------------------------------------------
    def send_rtc(self, code: str, data: Any | None = None) -> None:
        """Enqueue an RTC message."""
        self._rtc_queue.put((code, data))

    def stop(self) -> None:
        self._stop_event.set()

    # main loop -------------------------------------------------------------
    def run(self) -> None:
        while not self._stop_event.is_set():
            try:
                code, data = self._rtc_queue.get(timeout=self.interval)
            except queue.Empty:
                continue
            self.actions.append((code, data))
            if code == CMD_PROXY_CONFIG_CACHE_RELOAD:
                self.proxy_tasks.reload_proxy_cache_by_names(data)



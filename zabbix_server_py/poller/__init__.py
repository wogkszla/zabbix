"""Simplified poller thread."""

from __future__ import annotations

import threading
import time
from typing import Any, Iterable

from . import checks_internal


class Poller:
    """Periodically execute internal checks."""

    def __init__(self, items: Iterable[str], frequency: float = 1.0) -> None:
        self.items = list(items)
        self.frequency = frequency
        self.values: dict[str, Any] = {}
        self.poll_count = 0
        self._stop_event = threading.Event()

    def stop(self) -> None:
        self._stop_event.set()

    def poll_once(self) -> None:
        for key in self.items:
            try:
                self.values[key] = checks_internal.get_value_internal(key)
            except ValueError:
                self.values[key] = None
        self.poll_count += 1

    def run(self) -> None:
        """Run until :py:meth:`stop` is called."""
        while not self._stop_event.is_set():
            start = time.time()
            self.poll_once()
            elapsed = time.time() - start
            sleep_time = self.frequency - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

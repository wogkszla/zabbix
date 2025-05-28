"""Simplified timer thread from ``timer_thread``."""

from __future__ import annotations

import threading
import time


# ---------------------------------------------------------------------------
# stubs for maintenance processing
# ---------------------------------------------------------------------------

def update_maintenances() -> None:
    """Placeholder for maintenance update logic."""
    return None


def update_host_checks() -> None:
    """Placeholder for host maintenance update logic."""
    return None


class Timer:
    """Periodically update maintenances and host checks."""

    def __init__(self, interval: float = 60.0) -> None:
        self.interval = interval
        self._stop_event = threading.Event()
        self._wake_event = threading.Event()

    def stop(self) -> None:
        self._stop_event.set()
        self._wake_event.set()

    def trigger(self) -> None:
        """Request immediate execution."""
        self._wake_event.set()

    def run(self) -> None:
        while not self._stop_event.is_set():
            start = time.time()
            update_maintenances()
            update_host_checks()
            elapsed = time.time() - start
            wait_time = max(0.0, self.interval - elapsed)
            self._wake_event.wait(wait_time)
            self._wake_event.clear()


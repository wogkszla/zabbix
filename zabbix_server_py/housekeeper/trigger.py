"""Trigger housekeeper thread translated from ``trigger_housekeeper.c``."""

from __future__ import annotations

import threading

# ---------------------------------------------------------------------------
# stubs for problem cleanup
# ---------------------------------------------------------------------------

def remove_problems_without_triggers() -> None:
    """Placeholder for deleting problems without triggers."""
    return None


class TriggerHousekeeper:
    """Periodic trigger housekeeper thread."""

    def __init__(self, interval: float = 3600.0) -> None:
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
            remove_problems_without_triggers()
            self._wake_event.wait(self.interval)
            self._wake_event.clear()


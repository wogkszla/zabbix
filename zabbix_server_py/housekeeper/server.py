"""Housekeeper thread translated from ``housekeeper_server.c``."""

from __future__ import annotations

import threading


from .history import hk_history_compression_init, hk_history_compression_update


# ---------------------------------------------------------------------------
# stubs for database cleanup
# ---------------------------------------------------------------------------

def db_cleanup() -> None:
    """Placeholder for database cleanup logic."""
    return None


class Housekeeper:
    """Periodic housekeeping thread."""

    def __init__(self, interval: float = 3600.0, startup_delay: float = 0.0) -> None:
        self.interval = interval
        self.startup_delay = startup_delay
        self._stop_event = threading.Event()
        self._wake_event = threading.Event()

    def stop(self) -> None:
        self._stop_event.set()
        self._wake_event.set()

    def trigger(self) -> None:
        """Request immediate execution."""
        self._wake_event.set()

    # main loop ---------------------------------------------------------------
    def run(self) -> None:
        hk_history_compression_init()

        if self.startup_delay:
            self._wake_event.wait(self.startup_delay)
            self._wake_event.clear()

        while not self._stop_event.is_set():
            db_cleanup()
            hk_history_compression_update(None)
            self._wake_event.wait(self.interval)
            self._wake_event.clear()


"""Simplified configuration synchronisation loop."""

from __future__ import annotations

import threading
from typing import Callable


def zbx_db_connect() -> None:
    """Placeholder for the real database connection call."""
    return None


def zbx_dc_sync_configuration(reason: str) -> None:
    """Placeholder for configuration sync."""
    return None


class DBConfigServer:
    """Periodic configuration synchronisation thread."""

    def __init__(self, interval: float = 10.0) -> None:
        self.interval = interval
        self._reload_event = threading.Event()
        self._secrets_event = threading.Event()
        self._stop_event = threading.Event()
        self._wake_event = threading.Event()

    # signal handlers -----------------------------------------------------
    def request_reload(self) -> None:
        self._reload_event.set()
        self._wake_event.set()

    def request_secrets_reload(self) -> None:
        self._secrets_event.set()
        self._wake_event.set()

    def stop(self) -> None:
        self._stop_event.set()
        self._wake_event.set()

    # main loop -----------------------------------------------------------
    def run(self) -> None:
        """Run until :py:meth:`stop` is called."""
        zbx_db_connect()
        while not self._stop_event.is_set():
            if self._reload_event.is_set():
                self._reload_event.clear()
                zbx_dc_sync_configuration("reload")
            elif self._secrets_event.is_set():
                self._secrets_event.clear()
                zbx_dc_sync_configuration("secrets")
            else:
                zbx_dc_sync_configuration("periodic")
            self._wake_event.wait(self.interval)
            self._wake_event.clear()

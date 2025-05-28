"""Minimal escalator loop.

This module provides a greatly simplified version of the logic
implemented in ``escalator_thread`` from the original C source
``src/zabbix_server/escalator/escalator.c``.  The real code processes
pending escalations and generates alerts.  The Python variant merely
invokes a placeholder check function at a configurable interval so that
unit tests can verify the scheduling behaviour.
"""

from __future__ import annotations

import threading
import time


class Escalator:
    """Periodically execute escalation checks."""

    def __init__(self, frequency: float = 1.0) -> None:
        self.frequency = frequency
        self.check_count = 0
        self._running = False
        self._lock = threading.Lock()

    def _check_escalations(self) -> None:
        """Placeholder for escalation processing."""
        with self._lock:
            self.check_count += 1

    def stop(self) -> None:
        """Request the main loop to exit."""
        self._running = False

    def run(self) -> None:
        """Run the escalator loop.

        This mirrors the behaviour of ``escalator_thread`` by
        continually calling :py:meth:`_check_escalations` and sleeping
        between iterations.  The loop exits when :py:meth:`stop` is
        called.
        """
        self._running = True
        while self._running:
            start = time.time()
            self._check_escalations()
            elapsed = time.time() - start
            sleep_time = self.frequency - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)


from __future__ import annotations

"""Very small proxy group manager.

This is a Python approximation of ``pg_manager_thread`` found in
``pg_manager.c``. Only basic state management is implemented.
"""

import time
from threading import Thread
from typing import Optional

from .cache import Cache


class PGManager:
    """Simplified manager running in a thread."""

    STATE_INIT = 0
    STATE_RUNNING = 1
    STATE_STOPPED = 2

    def __init__(self, cache: Cache | None = None) -> None:
        self.cache = cache or Cache()
        self.state = self.STATE_INIT
        self.running = False
        self._thread: Optional[Thread] = None

    # public API ------------------------------------------------------------
    def start(self) -> None:
        self._thread = Thread(target=self.run, daemon=True)
        self._thread.start()

    def run(self) -> None:
        """Manager loop.

        Mirrors the structure of ``pg_manager_thread`` but omits all
        database and IPC interactions.
        """
        self.state = self.STATE_RUNNING
        self.running = True
        while self.running:
            time.sleep(0.05)
        self.state = self.STATE_STOPPED

    def stop(self) -> None:
        self.running = False
        if self._thread is not None:
            self._thread.join(timeout=1)

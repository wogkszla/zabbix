from __future__ import annotations

"""Simplified proxy poller implementation."""

import socket
import threading
import time
from dataclasses import dataclass
from typing import Iterable, List, Optional


@dataclass
class Proxy:
    """Description of a proxy to poll."""

    name: str
    addr: str = "127.0.0.1"
    port: int = 10051
    lastaccess: float = 0.0
    last_response: Optional[str] = None


class ProxyPoller:
    """Recreate the polling loop from ``proxypoller.c`` in Python."""

    def __init__(
        self,
        proxies: Iterable[Proxy],
        timeout: float = 1.0,
        frequency: float = 1.0,
    ) -> None:
        self.proxies: List[Proxy] = list(proxies)
        self.timeout = timeout
        self.frequency = frequency
        self._stop_event = threading.Event()

    # public API ------------------------------------------------------------
    def stop(self) -> None:
        self._stop_event.set()

    # internal helpers ------------------------------------------------------
    def _connect(self, proxy: Proxy) -> socket.socket:
        s = socket.create_connection((proxy.addr, proxy.port), timeout=self.timeout)
        return s

    def _poll_proxy(self, proxy: Proxy) -> None:
        try:
            with self._connect(proxy) as s:
                s.sendall(b"data")
                data = s.recv(1024)
                proxy.last_response = data.decode()
                proxy.lastaccess = time.time()
        except OSError:
            proxy.last_response = None

    # main loop -------------------------------------------------------------
    def poll_once(self) -> None:
        for proxy in self.proxies:
            self._poll_proxy(proxy)

    def run(self) -> None:
        while not self._stop_event.is_set():
            start = time.time()
            self.poll_once()
            elapsed = time.time() - start
            sleep_time = self.frequency - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

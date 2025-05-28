from __future__ import annotations

import json
import queue
import time
from typing import Any, Tuple


class HAManager:
    """Very small approximation of ``ha_manager_thread``."""

    # HA node status constants mirroring ``include/zbx_ha_constants.h``
    STATUS_HATIMEOUT = -3
    STATUS_ERROR = -2
    STATUS_UNKNOWN = -1
    STATUS_STANDBY = 0
    STATUS_STOPPED = 1
    STATUS_UNAVAILABLE = 2
    STATUS_ACTIVE = 3

    # message codes (not exhaustive)
    CMD_STATUS = "status"
    CMD_STOP = "stop"
    CMD_PAUSE = "pause"
    CMD_GET_NODES = "get_nodes"
    CMD_REMOVE_NODE = "remove_node"
    CMD_SET_FAILOVER_DELAY = "set_failover_delay"
    CMD_GET_FAILOVER_DELAY = "get_failover_delay"
    CMD_LOGLEVEL_INCREASE = "loglevel_increase"
    CMD_LOGLEVEL_DECREASE = "loglevel_decrease"
    CMD_REGISTER = "register"

    def __init__(self, node_name: str = "node", initial_status: int = STATUS_STANDBY,
                 failover_delay: int = 60) -> None:
        self.node_name = node_name
        self.status = initial_status
        self.failover_delay = failover_delay
        self.nodes = {node_name}
        self.running = False
        self.paused = False
        self._ticks = 0
        self._queue: queue.Queue[Tuple[str, Any, queue.Queue[Any]]] = queue.Queue()
        # used by tests to observe extra actions
        self.notifications: list[str] = []

    # public API ------------------------------------------------------------
    def send(self, code: str, data: Any | None = None) -> Any:
        """Send *code* to the manager and wait for the response."""
        resp: queue.Queue[Any] = queue.Queue()
        self._queue.put((code, data, resp))
        return resp.get(timeout=1)

    # main loop -------------------------------------------------------------
    def run(self) -> None:
        self.running = True
        while self.running:
            # automatic promotion when in standby
            if not self.paused and self.status == self.STATUS_STANDBY:
                if self._ticks >= self.failover_delay:
                    self.status = self.STATUS_ACTIVE
                else:
                    self._ticks += 1

            try:
                code, data, resp = self._queue.get(timeout=0.1)
            except queue.Empty:
                continue

            if self.paused and code not in {self.CMD_STATUS, self.CMD_STOP, self.CMD_PAUSE}:
                resp.put(None)
                continue

            if code == self.CMD_STATUS:
                resp.put({"status": self.status, "failover_delay": self.failover_delay})
            elif code == self.CMD_GET_NODES:
                resp.put(json.dumps(sorted(self.nodes)))
            elif code == self.CMD_REMOVE_NODE:
                node = str(data)
                if node == self.node_name:
                    resp.put({"error": "cannot remove self"})
                else:
                    removed = node in self.nodes
                    self.nodes.discard(node)
                    resp.put({"removed": removed})
            elif code == self.CMD_SET_FAILOVER_DELAY:
                self.failover_delay = int(data)
                self._ticks = 0
                resp.put("OK")
            elif code == self.CMD_GET_FAILOVER_DELAY:
                resp.put(self.failover_delay)
            elif code == self.CMD_PAUSE:
                self.paused = True
                resp.put("OK")
            elif code == self.CMD_STOP:
                self.running = False
                self.status = self.STATUS_STOPPED
                resp.put("OK")
            elif code == self.CMD_LOGLEVEL_INCREASE:
                self.notifications.append("log+1")
                resp.put("OK")
            elif code == self.CMD_LOGLEVEL_DECREASE:
                self.notifications.append("log-1")
                resp.put("OK")
            elif code == self.CMD_REGISTER:
                resp.put("OK")
            else:
                resp.put(None)

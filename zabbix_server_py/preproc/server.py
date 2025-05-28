"""Simplified preprocessing server translated from ``preproc_server.c``."""

from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass
from typing import Any

from zabbix_server_py.cachehistory.cache import HistoryCache


PP_VALUE_OPT_META = 0x01
FLAG_DISCOVERY_RULE = 0x01


@dataclass
class PreprocValueOpt:
    """Options associated with a value being preprocessed."""

    flags: int = 0
    lastlogsize: int = 0
    mtime: int = 0


class PreprocServer:
    """Very small approximation of the C preprocessing server."""

    def __init__(self, cache: HistoryCache | None = None) -> None:
        self.cache = cache or HistoryCache()
        self.lld_queue: list[dict[str, Any]] = []
        self.task_queue: queue.Queue[tuple[int, Any, int, int, PreprocValueOpt]] = queue.Queue()
        self._stop_event = threading.Event()

    # public API ------------------------------------------------------------
    def stop(self) -> None:
        self._stop_event.set()

    def submit(
        self,
        itemid: int,
        value: Any,
        value_type: int = 0,
        flags: int = 0,
        ts: int | None = None,
        value_opt: PreprocValueOpt | None = None,
    ) -> None:
        """Queue a value for preprocessing."""
        if ts is None:
            ts = int(time.time())
        if value_opt is None:
            value_opt = PreprocValueOpt()
        self.task_queue.put((itemid, value, value_type, flags, ts, value_opt))

    # internal helpers ------------------------------------------------------
    def _prepare_value(self, value: Any, value_opt: PreprocValueOpt) -> bool:
        """Validate value before processing."""
        if value is None and not (value_opt.flags & PP_VALUE_OPT_META):
            return False
        return True

    def _flush_value(
        self,
        itemid: int,
        value: Any,
        value_type: int,
        flags: int,
        ts: int,
        value_opt: PreprocValueOpt,
    ) -> None:
        if flags & FLAG_DISCOVERY_RULE:
            entry = {
                "itemid": itemid,
                "value": value,
                "timestamp": ts,
                "meta": bool(value_opt.flags & PP_VALUE_OPT_META),
                "lastlogsize": value_opt.lastlogsize,
                "mtime": value_opt.mtime,
            }
            self.lld_queue.append(entry)
        else:
            self.cache.add(itemid, value, timestamp=ts)

    # main loop -------------------------------------------------------------
    def run(self) -> None:
        while not self._stop_event.is_set():
            try:
                itemid, value, value_type, flags, ts, value_opt = self.task_queue.get(
                    timeout=0.1
                )
            except queue.Empty:
                continue
            if not self._prepare_value(value, value_opt):
                continue
            self._flush_value(itemid, value, value_type, flags, ts, value_opt)

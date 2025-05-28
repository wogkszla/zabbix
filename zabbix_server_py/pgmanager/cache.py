from __future__ import annotations

"""Lightweight proxy group cache.

This module is a very small subset of ``pg_cache.c``.
It implements :func:`pg_cache_init`, :func:`pg_cache_update_groups` and
:func:`pg_cache_update_proxies` in an in-memory form suitable for tests.
"""

from dataclasses import dataclass, field
from threading import Lock
from typing import Dict, List, Optional

# state constants mirroring ``pg_cache.h`` ------------------------------
PROXY_STATE_UNKNOWN = 0
PROXY_STATE_OFFLINE = 1
PROXY_STATE_ONLINE = 2

GROUP_STATE_UNKNOWN = 0
GROUP_STATE_OFFLINE = 1
GROUP_STATE_RECOVERING = 2
GROUP_STATE_ONLINE = 3
GROUP_STATE_DEGRADING = 4
GROUP_STATE_DISABLED = 5


@dataclass
class Proxy:
    """Representation of a proxy."""

    proxyid: int
    groupid: Optional[int] = None
    state: int = PROXY_STATE_UNKNOWN


@dataclass
class Group:
    """Representation of a proxy group."""

    groupid: int
    state: int = GROUP_STATE_DISABLED
    proxies: List[int] = field(default_factory=list)


class Cache:
    """In-memory cache.

    Only the functionality required by unit tests is provided.  The
    constructor loosely corresponds to ``pg_cache_init`` while the
    :py:meth:`refresh` method combines ``pg_cache_update_groups`` and
    ``pg_cache_update_proxies``.
    """

    def __init__(self) -> None:
        self.proxies: Dict[int, Proxy] = {}
        self.groups: Dict[int, Group] = {}
        self.hostmap_revision = 0
        self._lock = Lock()

    def refresh(self, proxies: List[Proxy], groups: List[Group]) -> None:
        """Replace cached data with *proxies* and *groups*.

        Parameters follow the data loaded by ``pgm_update`` in the C
        implementation.
        """
        with self._lock:
            self.hostmap_revision += 1
            self.proxies = {p.proxyid: p for p in proxies}
            self.groups = {g.groupid: Group(g.groupid, g.state, []) for g in groups}
            for proxy in proxies:
                if proxy.groupid is not None and proxy.groupid in self.groups:
                    self.groups[proxy.groupid].proxies.append(proxy.proxyid)

    def get_group(self, groupid: int) -> Optional[Group]:
        with self._lock:
            return self.groups.get(groupid)

    def get_proxy(self, proxyid: int) -> Optional[Proxy]:
        with self._lock:
            return self.proxies.get(proxyid)

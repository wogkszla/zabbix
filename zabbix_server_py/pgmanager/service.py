from __future__ import annotations

"""Utility helpers for proxy group manager service.

These routines roughly correspond to parts of ``pg_service.c`` such as
``pg_update_proxy_rtdata``.
"""

from .cache import Cache, PROXY_STATE_ONLINE, PROXY_STATE_OFFLINE


class PGService:
    """Very small service updating proxy runtime data."""

    def __init__(self, cache: Cache) -> None:
        self.cache = cache

    def update_proxy_state(self, proxyid: int, online: bool) -> None:
        """Set proxy state to online or offline.

        This is a small subset of ``pg_update_proxy_rtdata``.
        """
        proxy = self.cache.get_proxy(proxyid)
        if proxy is not None:
            proxy.state = PROXY_STATE_ONLINE if online else PROXY_STATE_OFFLINE

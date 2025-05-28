from __future__ import annotations

"""Helpers for proxy related tasks."""

class ProxyTasks:
    """Manage proxy related task operations."""

    def __init__(self) -> None:
        self.reload_log: list[str] = []

    # low level --------------------------------------------------------------
    def reload_proxy_cache(self, name: str) -> None:
        """Record proxy cache reload for *name*."""
        self.reload_log.append(name)

    def reload_all_proxy_caches(self) -> None:
        """Record reload request for all proxies."""
        self.reload_log.append("ALL")

    # public API -------------------------------------------------------------
    def reload_proxy_cache_by_names(self, names: list[str] | None) -> None:
        """Reload configuration cache on proxies listed in *names*.

        If *names* is ``None`` all proxies should be reloaded.
        """
        if names is None:
            self.reload_all_proxy_caches()
        else:
            for name in names:
                self.reload_proxy_cache(name)


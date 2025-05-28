"""Proxy configuration retrieval helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Dict, Tuple, Any


@dataclass
class ProxyConfig:
    """Simple configuration container."""

    revision: int
    data: Dict[str, Any] = field(default_factory=dict)


class ProxyConfigReader:
    """In-memory configuration provider.

    This mirrors functionality of ``proxyconfigread.c`` and provides
    replacements for ``zbx_proxyconfig_get_data`` and
    ``zbx_send_proxyconfig`` used in unit tests.
    """

    STATUS_EMPTY = 0
    STATUS_DATA = 1

    def __init__(self) -> None:
        self._configs: Dict[int, ProxyConfig] = {}

    # management -------------------------------------------------------------
    def set_proxy_config(self, proxy_id: int, revision: int, data: Dict[str, Any]) -> None:
        """Store configuration for *proxy_id*."""
        self._configs[proxy_id] = ProxyConfig(revision=revision, data=data)

    # public API ------------------------------------------------------------
    def zbx_proxyconfig_get_data(self, proxy_id: int, request: Dict[str, Any]) -> Tuple[str, int]:
        """Return configuration JSON and status.

        This corresponds to ``zbx_proxyconfig_get_data``. The *request*
        dictionary may contain ``config_revision`` used for change
        detection.  If the revision differs from the stored one the
        current configuration is encoded as JSON and returned with
        :pydata:`STATUS_DATA`.  Otherwise an empty JSON object is
        returned with :pydata:`STATUS_EMPTY`.
        """
        stored = self._configs.get(proxy_id)
        req_rev = int(request.get("config_revision", 0))
        if stored is None:
            return "{}", self.STATUS_EMPTY
        if stored.revision != req_rev:
            payload = {
                "config_revision": stored.revision,
                "data": stored.data,
            }
            return json.dumps(payload), self.STATUS_DATA
        return "{}", self.STATUS_EMPTY

    def zbx_send_proxyconfig(self, proxy_id: int, request: Dict[str, Any]) -> bytes:
        """Return configuration JSON encoded as bytes.

        Mirrors ``zbx_send_proxyconfig`` but simply calls
        :py:meth:`zbx_proxyconfig_get_data` and encodes the result.
        """
        json_text, _status = self.zbx_proxyconfig_get_data(proxy_id, request)
        return json_text.encode()

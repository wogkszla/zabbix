from __future__ import annotations

"""Trapper request dispatcher."""

from typing import Any, Dict

from .proxydata import ProxyDataManager
from .history_push import HistoryPush

ZBX_PROTO_VALUE_PROXY_DATA = "proxy data"
ZBX_PROTO_VALUE_HISTORY_PUSH = "history.push"


def zbx_trapper_process_request_server(
    request: str,
    data: Dict[str, Any],
    proxy_manager: ProxyDataManager,
    history_push: HistoryPush,
) -> bool:
    """Dispatch *request* to the appropriate handler.

    Returns ``True`` if the request was processed successfully or ``False`` if
    the type is unknown.
    """
    if request == ZBX_PROTO_VALUE_PROXY_DATA:
        proxy_manager.recv_proxy_data(data)
        return True
    if request == ZBX_PROTO_VALUE_HISTORY_PUSH:
        history_push.trapper_process_history_push(data)
        return True
    return False

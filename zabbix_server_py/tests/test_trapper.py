from zabbix_server_py.trapper.proxydata import ProxyDataManager
from zabbix_server_py.trapper.history_push import HistoryPush, ItemValue
from zabbix_server_py.trapper.server import (
    zbx_trapper_process_request_server,
    ZBX_PROTO_VALUE_PROXY_DATA,
    ZBX_PROTO_VALUE_HISTORY_PUSH,
)


def test_proxy_data_request_enqueues_data():
    proxy_mgr = ProxyDataManager()
    history = HistoryPush()
    request = {"a": 1}

    processed = zbx_trapper_process_request_server(
        ZBX_PROTO_VALUE_PROXY_DATA, request, proxy_mgr, history
    )

    assert processed is True
    queued = proxy_mgr.flush()
    assert queued == [request]
    assert proxy_mgr.flush() == []


def test_history_push_parses_items():
    proxy_mgr = ProxyDataManager()
    history = HistoryPush()
    request = {"data": [{"itemid": 1, "value": "a"}, {"itemid": 2, "value": 5}]}

    processed = zbx_trapper_process_request_server(
        ZBX_PROTO_VALUE_HISTORY_PUSH, request, proxy_mgr, history
    )

    assert processed is True
    items = history.flush()
    assert len(items) == 2
    assert items[0].itemid == 1
    assert items[0].value == "a"
    assert items[1].itemid == 2
    assert items[1].value == 5
    assert history.flush() == []


def test_unknown_request_returns_false():
    proxy_mgr = ProxyDataManager()
    history = HistoryPush()

    processed = zbx_trapper_process_request_server(
        "unknown", {}, proxy_mgr, history
    )

    assert processed is False
    assert proxy_mgr.flush() == []
    assert history.flush() == []

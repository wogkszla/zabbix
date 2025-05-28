from zabbix_server_py.rtc import RTCServer
from zabbix_server_py.ha import HAManager
import pytest


class DummyHA:
    def __init__(self) -> None:
        self.last: tuple[str, any] | None = None
        self.failover_delay = 60

    def send(self, code: str, data=None):
        self.last = (code, data)
        if code == HAManager.CMD_STATUS:
            return {"status": HAManager.STATUS_ACTIVE}
        if code == HAManager.CMD_GET_FAILOVER_DELAY:
            return self.failover_delay
        if code == HAManager.CMD_SET_FAILOVER_DELAY:
            self.failover_delay = int(data)
            return "OK"
        if code == HAManager.CMD_REMOVE_NODE:
            return {"removed": True}
        return "OK"


def test_ha_remove_node_dispatch():
    ha = DummyHA()
    srv = RTCServer(ha)
    srv.process("ha_remove_node=node2")
    assert ha.last == (HAManager.CMD_REMOVE_NODE, "node2")


def test_proxy_config_cache_reload_list():
    ha = DummyHA()
    srv = RTCServer(ha)
    srv.process("proxy_config_cache_reload=p1,p2")
    assert ("proxy_config_cache_reload", ["p1", "p2"]) in srv.actions


def test_ha_status_result():
    ha = DummyHA()
    srv = RTCServer(ha)
    res = srv.process("ha_status")
    assert ha.last == (HAManager.CMD_STATUS, None)
    assert res == {"status": HAManager.STATUS_ACTIVE}


def test_unknown_option_raises():
    srv = RTCServer(DummyHA())
    with pytest.raises(ValueError):
        srv.process("unknown_option")


def test_ha_set_failover_delay():
    ha = DummyHA()
    srv = RTCServer(ha)
    srv.process("ha_set_failover_delay=5")
    assert ha.last == (HAManager.CMD_SET_FAILOVER_DELAY, 5)

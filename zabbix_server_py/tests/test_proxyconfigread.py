import json
from zabbix_server_py.proxyconfigread import ProxyConfigReader


def test_get_data_returns_configuration():
    reader = ProxyConfigReader()
    reader.set_proxy_config(1, 2, {"settings": {"interval": 10}})

    data, status = reader.zbx_proxyconfig_get_data(1, {"config_revision": 0})

    assert status == ProxyConfigReader.STATUS_DATA
    payload = json.loads(data)
    assert payload["config_revision"] == 2
    assert payload["data"]["settings"]["interval"] == 10


def test_get_data_empty_when_revision_matches():
    reader = ProxyConfigReader()
    reader.set_proxy_config(1, 1, {"a": 1})

    reader.zbx_proxyconfig_get_data(1, {"config_revision": 0})
    data, status = reader.zbx_proxyconfig_get_data(1, {"config_revision": 1})

    assert status == ProxyConfigReader.STATUS_EMPTY
    assert json.loads(data) == {}


def test_send_proxyconfig_encodes_bytes():
    reader = ProxyConfigReader()
    reader.set_proxy_config(5, 3, {"v": 1})

    raw = reader.zbx_send_proxyconfig(5, {"config_revision": 0})

    assert isinstance(raw, bytes)
    payload = json.loads(raw.decode())
    assert payload["config_revision"] == 3

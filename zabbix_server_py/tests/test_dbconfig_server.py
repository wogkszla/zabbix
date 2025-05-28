import threading
import time

from zabbix_server_py.dbconfig import server as dbserver
from zabbix_server_py.dbconfig.server import DBConfigServer


def test_reload_signal_wakes_loop(monkeypatch):
    calls: list[str] = []

    def fake_connect():
        calls.append("connect")

    def fake_sync(reason: str):
        calls.append(reason)

    monkeypatch.setattr(dbserver, "zbx_db_connect", fake_connect)
    monkeypatch.setattr(dbserver, "zbx_dc_sync_configuration", fake_sync)

    srv = DBConfigServer(interval=1.0)
    t = threading.Thread(target=srv.run)
    t.start()

    # allow initial connect and sync
    time.sleep(0.2)
    srv.request_reload()
    time.sleep(0.2)
    srv.stop()
    t.join(timeout=1)

    assert "connect" in calls
    assert "reload" in calls

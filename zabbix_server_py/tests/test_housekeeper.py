import threading
import time

from zabbix_server_py.housekeeper.server import Housekeeper, db_cleanup
from zabbix_server_py.housekeeper.trigger import (
    TriggerHousekeeper,
    remove_problems_without_triggers,
)


def test_housekeeper_runs_periodically(monkeypatch):
    calls: list[float] = []

    def fake_cleanup():
        calls.append(time.time())

    monkeypatch.setattr(
        "zabbix_server_py.housekeeper.server.db_cleanup", fake_cleanup
    )

    hk = Housekeeper(interval=0.1, startup_delay=0)
    t = threading.Thread(target=hk.run, daemon=True)
    t.start()

    time.sleep(0.25)
    hk.stop()
    t.join(timeout=1)

    assert len(calls) >= 2


def test_trigger_housekeeper_runs(monkeypatch):
    calls: list[int] = []

    def fake_remove():
        calls.append(1)

    monkeypatch.setattr(
        "zabbix_server_py.housekeeper.trigger.remove_problems_without_triggers",
        fake_remove,
    )

    th = TriggerHousekeeper(interval=0.1)
    t = threading.Thread(target=th.run, daemon=True)
    t.start()

    time.sleep(0.25)
    th.stop()
    t.join(timeout=1)

    assert len(calls) >= 2


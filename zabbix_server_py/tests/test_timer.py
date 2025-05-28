import threading
import time

from zabbix_server_py.timer import Timer


def test_timer_runs_periodically(monkeypatch):
    maint_calls: list[float] = []
    host_calls: list[float] = []

    def fake_update_maintenances():
        maint_calls.append(time.time())

    def fake_update_host_checks():
        host_calls.append(time.time())

    monkeypatch.setattr(
        "zabbix_server_py.timer.timer.update_maintenances", fake_update_maintenances
    )
    monkeypatch.setattr(
        "zabbix_server_py.timer.timer.update_host_checks", fake_update_host_checks
    )

    tmr = Timer(interval=0.1)
    t = threading.Thread(target=tmr.run, daemon=True)
    t.start()

    time.sleep(0.25)
    tmr.stop()
    t.join(timeout=1)

    assert len(maint_calls) >= 2
    assert len(host_calls) >= 2


def test_timer_trigger(monkeypatch):
    calls: list[str] = []

    def fake_update_maintenances():
        calls.append("m")

    def fake_update_host_checks():
        calls.append("h")

    monkeypatch.setattr(
        "zabbix_server_py.timer.timer.update_maintenances", fake_update_maintenances
    )
    monkeypatch.setattr(
        "zabbix_server_py.timer.timer.update_host_checks", fake_update_host_checks
    )

    tmr = Timer(interval=10)
    t = threading.Thread(target=tmr.run, daemon=True)
    t.start()

    time.sleep(0.05)
    tmr.trigger()
    time.sleep(0.1)
    tmr.stop()
    t.join(timeout=1)

    assert calls

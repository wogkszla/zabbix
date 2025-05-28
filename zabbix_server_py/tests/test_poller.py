from threading import Thread
import time

from zabbix_server_py.poller import Poller


def test_poll_once_collects_values():
    p = Poller(["zabbix[triggers]", "zabbix[host,,items]"])
    p.poll_once()
    assert p.values["zabbix[triggers]"] == 3
    assert p.values["zabbix[host,,items]"] == 7


def test_poller_runs_periodically():
    p = Poller(["zabbix[triggers]"], frequency=0.1)
    t = Thread(target=p.run, daemon=True)
    t.start()
    time.sleep(0.35)
    p.stop()
    t.join(timeout=1)
    assert p.poll_count >= 3

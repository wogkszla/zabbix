from threading import Thread
import time

from zabbix_server_py.escalator.escalator import Escalator


def test_escalator_runs_periodically():
    esc = Escalator(frequency=0.1)
    t = Thread(target=esc.run, daemon=True)
    t.start()

    time.sleep(0.35)
    esc.stop()
    t.join(timeout=1)

    assert esc.check_count >= 3


def test_escalator_stops():
    esc = Escalator(frequency=0.1)
    t = Thread(target=esc.run, daemon=True)
    t.start()

    time.sleep(0.15)
    esc.stop()
    count = esc.check_count
    t.join(timeout=1)

    time.sleep(0.2)
    assert esc.check_count == count

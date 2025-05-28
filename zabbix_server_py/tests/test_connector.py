from threading import Thread
import time

from zabbix_server_py.connector.manager import ConnectorManager
from zabbix_server_py.connector.worker import ConnectorWorker


def test_worker_processes_request():
    manager = ConnectorManager()
    worker = ConnectorWorker(manager)

    tm = Thread(target=manager.run, daemon=True)
    tw = Thread(target=worker.run, daemon=True)
    tm.start()
    tw.start()

    manager.add_request("ping")

    for _ in range(20):
        if "OK:ping" in manager.received_results:
            break
        time.sleep(0.1)

    assert "OK:ping" in manager.received_results

    manager.add_request("STOP")
    tw.join(timeout=1)
    tm.join(timeout=1)


def test_multiple_requests():
    manager = ConnectorManager()
    worker = ConnectorWorker(manager)

    tm = Thread(target=manager.run, daemon=True)
    tw = Thread(target=worker.run, daemon=True)
    tm.start()
    tw.start()

    for i in range(3):
        manager.add_request(f"t{i}")

    for _ in range(30):
        if len(manager.received_results) >= 3:
            break
        time.sleep(0.1)

    assert manager.received_results == ["OK:t0", "OK:t1", "OK:t2"]

    manager.add_request("STOP")
    tw.join(timeout=1)
    tm.join(timeout=1)

from threading import Thread
import time

from zabbix_server_py.lld import parse_rule, discover_items, LLDManager, LLDWorker


def test_parse_rule():
    rule = parse_rule("id=1;items=a,b")
    assert rule["id"] == 1
    assert rule["items"] == "a,b"


def test_discover_items():
    items = discover_items({"items": "x,y,z"})
    assert items == ["x", "y", "z"]


def test_worker_processes_rule():
    manager = LLDManager()
    worker = LLDWorker(manager)

    tm = Thread(target=manager.run, daemon=True)
    tw = Thread(target=worker.run, daemon=True)
    tm.start()
    tw.start()

    manager.add_rule("items=p,q")

    for _ in range(20):
        if ["p", "q"] in manager.results:
            break
        time.sleep(0.1)

    assert ["p", "q"] in manager.results

    manager.stop()
    tw.join(timeout=1)
    tm.join(timeout=1)

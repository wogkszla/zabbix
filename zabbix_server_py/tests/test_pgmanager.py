from threading import Thread
import time

from zabbix_server_py.pgmanager.cache import (
    Cache,
    Group,
    Proxy,
)
from zabbix_server_py.pgmanager.manager import PGManager


def test_cache_refresh_replaces_content():
    cache = Cache()

    cache.refresh([Proxy(1, groupid=1)], [Group(1)])
    assert cache.get_group(1).proxies == [1]

    # refresh with completely new data
    cache.refresh([Proxy(2, groupid=2)], [Group(2)])
    assert cache.get_group(1) is None
    assert cache.get_group(2).proxies == [2]
    assert cache.hostmap_revision == 2


def test_manager_state_transition():
    cache = Cache()
    manager = PGManager(cache)
    t = Thread(target=manager.run, daemon=True)
    t.start()

    for _ in range(20):
        if manager.state == PGManager.STATE_RUNNING:
            break
        time.sleep(0.05)

    assert manager.state == PGManager.STATE_RUNNING

    manager.stop()
    t.join(timeout=1)
    assert manager.state == PGManager.STATE_STOPPED

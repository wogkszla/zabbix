from __future__ import annotations

import threading
import time

from zabbix_server_py.taskmanager.proxy_tasks import ProxyTasks
from zabbix_server_py.taskmanager.server import TaskManagerThread
from zabbix_server_py.rtc.server import CMD_PROXY_CONFIG_CACHE_RELOAD


def test_reload_proxy_cache_by_names():
    tasks = ProxyTasks()
    tasks.reload_proxy_cache_by_names(["p1", "p2"])
    assert tasks.reload_log == ["p1", "p2"]


def test_taskmanager_handles_rtc_reload():
    tasks = ProxyTasks()
    srv = TaskManagerThread(proxy_tasks=tasks, interval=0.05)
    t = threading.Thread(target=srv.run, daemon=True)
    t.start()

    srv.send_rtc(CMD_PROXY_CONFIG_CACHE_RELOAD, ["px"])
    time.sleep(0.1)
    srv.stop()
    t.join(timeout=1)

    assert tasks.reload_log == ["px"]
    assert (CMD_PROXY_CONFIG_CACHE_RELOAD, ["px"]) in srv.actions


def test_taskmanager_reload_all():
    tasks = ProxyTasks()
    srv = TaskManagerThread(proxy_tasks=tasks, interval=0.05)
    t = threading.Thread(target=srv.run, daemon=True)
    t.start()

    srv.send_rtc(CMD_PROXY_CONFIG_CACHE_RELOAD, None)
    time.sleep(0.1)
    srv.stop()
    t.join(timeout=1)

    assert tasks.reload_log == ["ALL"]


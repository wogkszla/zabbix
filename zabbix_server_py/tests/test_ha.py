from threading import Thread
import time

from zabbix_server_py.ha import (
    HAManager,
    zbx_ha_get_nodes,
    zbx_ha_get_failover_delay,
    zbx_ha_set_failover_delay,
    zbx_ha_remove_node,
)


def test_state_transition_and_stop():
    manager = HAManager(initial_status=HAManager.STATUS_STANDBY, failover_delay=2)
    t = Thread(target=manager.run, daemon=True)
    t.start()

    # wait for promotion to ACTIVE
    for _ in range(20):
        status = manager.send(HAManager.CMD_STATUS)["status"]
        if status == HAManager.STATUS_ACTIVE:
            break
        time.sleep(0.05)
    assert status == HAManager.STATUS_ACTIVE

    manager.send(HAManager.CMD_STOP)
    t.join(timeout=1)
    assert not manager.running
    assert manager.status == HAManager.STATUS_STOPPED


def test_message_handling():
    manager = HAManager(initial_status=HAManager.STATUS_ACTIVE)
    manager.nodes.add("node2")
    t = Thread(target=manager.run, daemon=True)
    t.start()

    assert zbx_ha_get_nodes(manager) == '["node", "node2"]'

    res = zbx_ha_remove_node(manager, "node2")
    assert res == {"removed": True}
    assert zbx_ha_get_nodes(manager) == '["node"]'

    zbx_ha_set_failover_delay(manager, 5)
    assert zbx_ha_get_failover_delay(manager) == 5

    manager.send(HAManager.CMD_STOP)
    t.join(timeout=1)


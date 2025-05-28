"""Minimal helpers wrapping HA manager commands."""

from __future__ import annotations

from .manager import HAManager

__all__ = [
    "HAManager",
    "zbx_ha_get_nodes",
    "zbx_ha_remove_node",
    "zbx_ha_set_failover_delay",
    "zbx_ha_get_failover_delay",
]


def zbx_ha_get_nodes(manager: HAManager) -> str:
    """Return JSON list of known nodes."""
    return manager.send(HAManager.CMD_GET_NODES)


def zbx_ha_remove_node(manager: HAManager, node: str):
    """Remove *node* from the cluster."""
    return manager.send(HAManager.CMD_REMOVE_NODE, node)


def zbx_ha_set_failover_delay(manager: HAManager, delay: int) -> str:
    """Set failover delay."""
    return manager.send(HAManager.CMD_SET_FAILOVER_DELAY, delay)


def zbx_ha_get_failover_delay(manager: HAManager) -> int:
    """Return current failover delay."""
    return manager.send(HAManager.CMD_GET_FAILOVER_DELAY)

"""Internal check helpers for the Poller."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Tuple


# ---------------------------------------------------------------------------
# Stubs replicating C functions from checks_internal_server.c
# ---------------------------------------------------------------------------

_TRIGGER_COUNT = 3
_ITEM_COUNT = 7
_ITEM_UNSUPPORTED_COUNT = 2


@dataclass
class PBMemInfo:
    """Simplified proxy buffer memory information."""

    mem_total: int = 0
    mem_used: int = 0


@dataclass
class PBStateInfo:
    """Simplified proxy buffer state information."""

    state: int = 0
    changes_num: int = 0


def pb_get_mem_info() -> PBMemInfo:
    """Return dummy proxy buffer memory statistics."""

    return PBMemInfo()


def pb_get_state_info() -> PBStateInfo:
    """Return dummy proxy buffer state statistics."""

    return PBStateInfo()


# ---------------------------------------------------------------------------
# Internal item processing
# ---------------------------------------------------------------------------

def _parse_key(key: str) -> Tuple[str, List[str]]:
    if not key.startswith("zabbix[") or not key.endswith("]"):
        raise ValueError(f"Invalid key format: {key}")
    inner = key[len("zabbix[") : -1]
    parts = [p for p in inner.split(",")]
    if not parts:
        raise ValueError("Empty internal check")
    return parts[0], parts[1:]


def get_value_internal(key: str) -> Any:
    """Return a value for a simplified internal check."""

    param1, params = _parse_key(key)

    if param1 == "triggers":
        if params:
            raise ValueError("Invalid number of parameters")
        return _TRIGGER_COUNT

    if param1 == "host":
        if len(params) != 2:
            raise ValueError("Invalid number of parameters")
        _host = params[0]
        param3 = params[1]
        if param3 == "items":
            return _ITEM_COUNT
        if param3 == "items_unsupported":
            return _ITEM_UNSUPPORTED_COUNT
        if param3 == "maintenance":
            return 0
        raise ValueError("Invalid third parameter")

    raise ValueError(f"Unsupported internal check: {param1}")

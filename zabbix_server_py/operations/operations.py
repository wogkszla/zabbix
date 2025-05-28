"""Simplified action operation processing."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, List, Dict


# Supported operation types ----------------------------------------------------

OPERATION_TYPE_MESSAGE = "message"
OPERATION_TYPE_COMMAND = "command"


@dataclass
class Operation:
    """Representation of a single action operation."""

    type: str
    params: Dict[str, Any] = field(default_factory=dict)


def process_operations(
    event: Any,
    operations: List[Operation],
    executor: Callable[[Operation, Any], None] | None = None,
) -> None:
    """Execute operations for *event*.

    This is a very small subset of the logic implemented in the C
    function ``process_operations`` from ``src/zabbix_server/operations/operations.c``.
    The Python version merely validates operation types and invokes the
    provided *executor* callback.
    """

    for op in operations:
        if op.type not in (OPERATION_TYPE_MESSAGE, OPERATION_TYPE_COMMAND):
            raise ValueError(f"unsupported operation type: {op.type}")

        if executor is not None:
            executor(op, event)

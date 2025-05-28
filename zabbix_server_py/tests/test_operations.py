import pytest
from zabbix_server_py.operations.operations import (
    Operation,
    OPERATION_TYPE_MESSAGE,
    OPERATION_TYPE_COMMAND,
    process_operations,
)


class DummyEvent:
    def __init__(self, eventid: int) -> None:
        self.eventid = eventid


def test_process_operations_executes_all_operations():
    event = DummyEvent(1)
    ops = [
        Operation(OPERATION_TYPE_MESSAGE, {"user": "u1", "text": "hi"}),
        Operation(OPERATION_TYPE_COMMAND, {"cmd": "echo"}),
    ]
    calls: list[tuple[str, dict, int]] = []

    def exec_op(op: Operation, ev: DummyEvent) -> None:
        calls.append((op.type, op.params, ev.eventid))

    process_operations(event, ops, exec_op)

    assert calls == [
        (OPERATION_TYPE_MESSAGE, {"user": "u1", "text": "hi"}, 1),
        (OPERATION_TYPE_COMMAND, {"cmd": "echo"}, 1),
    ]


def test_process_operations_unknown_type():
    event = DummyEvent(2)
    ops = [Operation("bad", {})]

    with pytest.raises(ValueError):
        process_operations(event, ops)


def test_process_operations_propagates_executor_error():
    event = DummyEvent(3)
    ops = [Operation(OPERATION_TYPE_MESSAGE, {})]

    def boom(_op: Operation, _ev: DummyEvent) -> None:
        raise RuntimeError("fail")

    with pytest.raises(RuntimeError):
        process_operations(event, ops, boom)

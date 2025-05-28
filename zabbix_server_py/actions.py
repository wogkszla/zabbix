"""Simplified action processing translated from C.

This module provides a minimal Python version of selected logic from
src/zabbix_server/actions/actions.c.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List

# Constants derived from C headers
EVENT_SOURCE_TRIGGERS = 0
EVENT_SOURCE_DISCOVERY = 1
EVENT_SOURCE_AUTOREGISTRATION = 2
EVENT_SOURCE_INTERNAL = 3
EVENT_SOURCE_SERVICE = 4

EVENT_OBJECT_TRIGGER = 0
EVENT_OBJECT_ITEM = 4
EVENT_OBJECT_LLDRULE = 5

TRIGGER_VALUE_OK = 0
TRIGGER_STATE_NORMAL = 0
ITEM_STATE_NORMAL = 0

ZBX_FLAGS_DB_EVENT_CREATE = 0x0001
ZBX_FLAGS_DB_EVENT_NO_ACTION = 0x0002


@dataclass
class Event:
    """Representation of ``zbx_db_event``."""

    eventid: int
    source: int
    object: int
    value: int
    flags: int = 0


@dataclass
class Action:
    """Action definition."""

    actionid: int
    eventsource: int
    condition: Callable[[Event], bool] = lambda _e: True
    operations: List[str] = field(default_factory=list)


def is_recovery_event(event: Event) -> bool:
    """Return True if event is a recovery event.

    Translated from ``is_recovery_event()``.
    """
    if event.source == EVENT_SOURCE_TRIGGERS:
        return event.object == EVENT_OBJECT_TRIGGER and event.value == TRIGGER_VALUE_OK

    if event.source == EVENT_SOURCE_INTERNAL:
        if event.object == EVENT_OBJECT_TRIGGER and event.value == TRIGGER_STATE_NORMAL:
            return True
        if event.object == EVENT_OBJECT_ITEM and event.value == ITEM_STATE_NORMAL:
            return True
        if event.object == EVENT_OBJECT_LLDRULE and event.value == ITEM_STATE_NORMAL:
            return True

    return False


def is_escalation_event(event: Event) -> bool:
    """Determine if an event can start escalation.

    Translated from ``is_escalation_event()``.
    """
    if is_recovery_event(event):
        return False
    if event.flags & ZBX_FLAGS_DB_EVENT_NO_ACTION:
        return False
    if not (event.flags & ZBX_FLAGS_DB_EVENT_CREATE):
        return False
    return True


def execute_operations(event: Event, action: Action, log: list[str] | None = None) -> None:
    """Execute operations attached to the action.

    Translated from ``execute_operations()``.
    """
    if log is None:
        return

    for op in action.operations:
        log.append(f"action{action.actionid}:{op}:event{event.eventid}")


def process_actions(events: List[Event], actions: List[Action], log: list[str] | None = None) -> None:
    """Process actions for a list of events.

    This is a very small subset of ``process_actions()`` from the C code.
    """
    for event in events:
        if not is_escalation_event(event):
            continue
        for action in actions:
            if action.eventsource != event.source:
                continue
            if action.condition(event):
                execute_operations(event, action, log)

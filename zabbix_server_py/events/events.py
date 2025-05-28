"""Minimal event creation and recovery handling.

This module implements a very small subset of ``src/zabbix_server/events/events.c``.
Only the logic required for unit testing is provided.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from zabbix_server_py.actions import (
    EVENT_OBJECT_TRIGGER,
    EVENT_SOURCE_TRIGGERS,
    TRIGGER_STATE_NORMAL,
    TRIGGER_VALUE_OK,
)

# Additional constants ---------------------------------------------------------

TRIGGER_VALUE_PROBLEM = 1

FLAGS_RECALCULATE_PROBLEM_COUNT = 0x01


@dataclass
class Event:
    """Simplified representation of ``zbx_db_event``."""

    eventid: int
    source: int
    object: int
    objectid: int
    value: int
    clock: int
    name: str | None = None
    flags: int = 0


@dataclass
class EventRecovery:
    """Information about a recovered problem event."""

    eventid: int
    objectid: int
    r_event: Event
    correlationid: int = 0
    c_eventid: int = 0
    userid: int = 0
    ts: int = 0


@dataclass
class TriggerDiff:
    """Change set entry for a trigger."""

    triggerid: int
    priority: int
    flags: int
    value: int
    state: int = TRIGGER_STATE_NORMAL


_events: List[Event] = []
_event_recovery: Dict[int, EventRecovery] = {}


def reset() -> None:
    """Clear internal storage used by the module."""

    _events.clear()
    _event_recovery.clear()


def add_event(
    source: int,
    object: int,
    objectid: int,
    clock: int,
    value: int,
    name: str | None = None,
) -> Event:
    """Create and store an event."""

    eventid = len(_events) + 1
    event = Event(
        eventid=eventid,
        source=source,
        object=object,
        objectid=objectid,
        value=value,
        clock=clock,
        name=name,
        flags=0,
    )
    _events.append(event)
    return event


def close_trigger_event(
    eventid: int,
    objectid: int,
    clock: int,
    userid: int = 0,
    correlationid: int = 0,
    c_eventid: int = 0,
    name: str | None = None,
) -> Event:
    """Create a recovery event and remember correlation information."""

    r_event = add_event(
        EVENT_SOURCE_TRIGGERS,
        EVENT_OBJECT_TRIGGER,
        objectid,
        clock,
        TRIGGER_VALUE_OK,
        name,
    )
    recovery = EventRecovery(
        eventid=eventid,
        objectid=objectid,
        r_event=r_event,
        correlationid=correlationid,
        c_eventid=c_eventid,
        userid=userid,
        ts=clock,
    )
    _event_recovery[eventid] = recovery
    return r_event


def append_trigger_diff(
    diffs: Dict[int, TriggerDiff],
    triggerid: int,
    priority: int,
    value: int,
) -> TriggerDiff:
    """Add or update a trigger diff entry using a dictionary."""

    diff = diffs.get(triggerid)
    if diff is None:
        diff = TriggerDiff(
            triggerid=triggerid,
            priority=priority,
            flags=FLAGS_RECALCULATE_PROBLEM_COUNT,
            value=value,
        )
        diffs[triggerid] = diff
    else:
        diff.flags |= FLAGS_RECALCULATE_PROBLEM_COUNT
    return diff


def get_events() -> List[Event]:
    """Return a copy of collected events."""

    return list(_events)


def get_event_recovery() -> Dict[int, EventRecovery]:
    """Return a copy of recovery information."""

    return dict(_event_recovery)

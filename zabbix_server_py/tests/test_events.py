from zabbix_server_py.events.events import (
    add_event,
    append_trigger_diff,
    close_trigger_event,
    get_event_recovery,
    get_events,
    reset,
    FLAGS_RECALCULATE_PROBLEM_COUNT,
    TRIGGER_VALUE_PROBLEM,
)
from zabbix_server_py.actions import EVENT_SOURCE_TRIGGERS, EVENT_OBJECT_TRIGGER


def setup_function(_func):
    reset()


def test_add_event():
    event = add_event(
        EVENT_SOURCE_TRIGGERS,
        EVENT_OBJECT_TRIGGER,
        1,
        100,
        TRIGGER_VALUE_PROBLEM,
        name="problem",
    )
    events = get_events()
    assert len(events) == 1
    assert events[0] == event
    assert event.objectid == 1


def test_close_trigger_event_records_recovery():
    ev = add_event(EVENT_SOURCE_TRIGGERS, EVENT_OBJECT_TRIGGER, 1, 100, TRIGGER_VALUE_PROBLEM)
    ok_event = close_trigger_event(ev.eventid, 1, 200, userid=5)
    events = get_events()
    assert ok_event in events
    rec = get_event_recovery()[ev.eventid]
    assert rec.userid == 5
    assert rec.r_event == ok_event


def test_append_trigger_diff_uses_dict():
    diffs = {}
    append_trigger_diff(diffs, 10, priority=2, value=TRIGGER_VALUE_PROBLEM)
    append_trigger_diff(diffs, 10, priority=2, value=TRIGGER_VALUE_PROBLEM)
    assert len(diffs) == 1
    diff = diffs[10]
    assert diff.flags & FLAGS_RECALCULATE_PROBLEM_COUNT

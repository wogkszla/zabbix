from zabbix_server_py.actions import (
    Action,
    Event,
    EVENT_SOURCE_TRIGGERS,
    EVENT_OBJECT_TRIGGER,
    TRIGGER_VALUE_OK,
    ZBX_FLAGS_DB_EVENT_CREATE,
    is_recovery_event,
    process_actions,
)


def test_is_recovery_event():
    event = Event(
        eventid=1,
        source=EVENT_SOURCE_TRIGGERS,
        object=EVENT_OBJECT_TRIGGER,
        value=TRIGGER_VALUE_OK,
        flags=ZBX_FLAGS_DB_EVENT_CREATE,
    )
    assert is_recovery_event(event)


def test_process_actions_executes_operations():
    event = Event(
        eventid=2,
        source=EVENT_SOURCE_TRIGGERS,
        object=EVENT_OBJECT_TRIGGER,
        value=1,
        flags=ZBX_FLAGS_DB_EVENT_CREATE,
    )
    action = Action(actionid=100, eventsource=EVENT_SOURCE_TRIGGERS, operations=["notify"]) 
    log: list[str] = []

    process_actions([event], [action], log)

    assert log == ["action100:notify:event2"]


def test_non_escalation_event_skipped():
    event = Event(
        eventid=3,
        source=EVENT_SOURCE_TRIGGERS,
        object=EVENT_OBJECT_TRIGGER,
        value=TRIGGER_VALUE_OK,
        flags=ZBX_FLAGS_DB_EVENT_CREATE,
    )
    action = Action(actionid=200, eventsource=EVENT_SOURCE_TRIGGERS, operations=["op"]) 
    log: list[str] = []

    process_actions([event], [action], log)

    assert log == []

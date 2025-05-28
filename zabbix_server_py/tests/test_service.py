from zabbix_server_py.service import (
    Service,
    ServiceRule,
    ServiceAction,
    ServiceUpdate,
    ServiceManager,
    SERVICE_STATUS_RULE_TYPE_N_GE,
)


def test_rule_matching_count():
    child1 = Service(serviceid=1, status=4)
    child2 = Service(serviceid=2, status=3)
    child3 = Service(serviceid=3, status=1)
    parent = Service(serviceid=10, children=[child1, child2, child3])
    rule = ServiceRule(
        service_ruleid=1,
        type=SERVICE_STATUS_RULE_TYPE_N_GE,
        limit_value=2,
        limit_status=3,
        new_status=5,
    )
    manager = ServiceManager()

    status = manager.get_rule_status(parent, rule)

    assert status == 5


def test_service_action_executes_operations():
    service = Service(serviceid=1, status=2, name="svc")
    update = ServiceUpdate(service=service)
    action = ServiceAction(
        actionid=100,
        formula="1 and 2",
        conditions={
            1: lambda u: u.service.serviceid == 1,
            2: lambda u: u.service.status >= 2,
        },
        operations=["notify"],
    )
    manager = ServiceManager(actions=[action])
    log: list[str] = []

    manager.process_update(update, log)

    assert log == ["action100:notify:service1"]


from __future__ import annotations

"""Very small service manager implementation."""

from dataclasses import dataclass, field
from typing import List

from .actions import ServiceAction, ServiceUpdate


# constants matching service_manager_impl.h ------------------------------------
SERVICE_STATUS_OK = -1

SERVICE_STATUS_PROPAGATION_AS_IS = 0
SERVICE_STATUS_PROPAGATION_INCREASE = 1
SERVICE_STATUS_PROPAGATION_DECREASE = 2
SERVICE_STATUS_PROPAGATION_IGNORE = 3
SERVICE_STATUS_PROPAGATION_FIXED = 4

SERVICE_STATUS_RULE_TYPE_N_GE = 0

ZBX_SERVICE_STATUS_CALC_SET_OK = 0
ZBX_SERVICE_STATUS_CALC_MOST_CRITICAL_ALL = 1
ZBX_SERVICE_STATUS_CALC_MOST_CRITICAL_ONE = 2

TRIGGER_SEVERITY_COUNT = 6


@dataclass
class ServiceRule:
    service_ruleid: int
    type: int
    limit_value: int
    limit_status: int
    new_status: int


@dataclass
class Service:
    serviceid: int
    name: str = ""
    status: int = SERVICE_STATUS_OK
    children: List["Service"] = field(default_factory=list)
    weight: int = 0
    propagation_rule: int = SERVICE_STATUS_PROPAGATION_AS_IS
    propagation_value: int = 0
    algorithm: int = ZBX_SERVICE_STATUS_CALC_SET_OK
    status_rules: List[ServiceRule] = field(default_factory=list)


class ServiceManager:
    """Execute service rules and actions."""

    def __init__(self, actions: List[ServiceAction] | None = None) -> None:
        self.actions = actions or []

    # rule evaluation -----------------------------------------------------
    def get_status(self, service: Service) -> int:
        if service.propagation_rule == SERVICE_STATUS_PROPAGATION_IGNORE:
            raise ValueError("ignored")

        if service.status == SERVICE_STATUS_OK:
            return SERVICE_STATUS_OK

        if service.propagation_rule == SERVICE_STATUS_PROPAGATION_AS_IS:
            return service.status
        if service.propagation_rule == SERVICE_STATUS_PROPAGATION_INCREASE:
            res = service.status + service.propagation_value
            return min(res, TRIGGER_SEVERITY_COUNT - 1)
        if service.propagation_rule == SERVICE_STATUS_PROPAGATION_DECREASE:
            res = service.status - service.propagation_value
            return max(res, SERVICE_STATUS_OK + 1)
        if service.propagation_rule == SERVICE_STATUS_PROPAGATION_FIXED:
            return service.propagation_value
        return service.status

    def _children_by_status(self, service: Service, status_limit: int) -> tuple[list[Service], int, int]:
        children: list[Service] = []
        total_weight = 0
        total_num = 0
        for child in service.children:
            child_status = self.get_status(child)
            total_weight += child.weight
            total_num += 1
            if child_status >= status_limit:
                children.append(child)
        return children, total_weight, total_num

    def get_rule_status(self, service: Service, rule: ServiceRule) -> int:
        if rule.type != SERVICE_STATUS_RULE_TYPE_N_GE:
            return SERVICE_STATUS_OK
        status_limit = rule.limit_status
        children, _total_weight, _total_num = self._children_by_status(service, status_limit)
        if len(children) >= rule.limit_value:
            return rule.new_status
        return SERVICE_STATUS_OK

    # action processing ---------------------------------------------------
    def match_actions(self, update: ServiceUpdate) -> List[ServiceAction]:
        matched = []
        for action in self.actions:
            if action.match(update):
                matched.append(action)
        return matched

    def process_update(self, update: ServiceUpdate, log: List[str] | None = None) -> None:
        for action in self.match_actions(update):
            action.execute(update, log)


from __future__ import annotations

"""Simplified service action processing."""

from dataclasses import dataclass, field
from typing import Callable, Dict, List


@dataclass
class ServiceUpdate:
    """Very small subset of ``zbx_service_update_t``."""

    service: "Service"


@dataclass
class ServiceAction:
    """Action executed on matching service updates."""

    actionid: int
    formula: str = "1"
    conditions: Dict[int, Callable[[ServiceUpdate], bool]] = field(default_factory=dict)
    operations: List[str] = field(default_factory=list)

    def match(self, update: ServiceUpdate) -> bool:
        """Return True if *update* matches this action."""
        local_env = {str(cid): cond(update) for cid, cond in self.conditions.items()}
        try:
            return bool(eval(self.formula, {}, local_env))
        except Exception:
            return False

    def execute(self, update: ServiceUpdate, log: List[str] | None = None) -> None:
        """Execute attached operations for *update*."""
        if log is None:
            return
        for op in self.operations:
            log.append(f"action{self.actionid}:{op}:service{update.service.serviceid}")


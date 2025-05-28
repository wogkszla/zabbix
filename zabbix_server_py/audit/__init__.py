"""Simple audit logging utilities for the Python server rewrite."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class AuditEntry:
    """Single audit log entry."""

    resource: str
    action: str
    data: Dict[str, Any] = field(default_factory=dict)


class AuditLogger:
    """Collects audit log entries in memory."""

    def __init__(self) -> None:
        self.entries: List[AuditEntry] = []

    def log(self, resource: str, action: str, **data: Any) -> None:
        entry = AuditEntry(resource=resource, action=action, data=data)
        self.entries.append(entry)


# Configuration reload auditing -------------------------------------------------

def proxy_config_reload(logger: AuditLogger, proxy_id: int, name: str) -> None:
    """Record that a proxy configuration was reloaded."""
    logger.log("proxy", "config_reload", id=proxy_id, name=name)


# Settings auditing -------------------------------------------------------------

def settings_create_entry(logger: AuditLogger, action: str) -> None:
    """Create audit entry for settings action."""
    logger.log("settings", action)


def settings_update_field_str(
    logger: AuditLogger, key: str, old_value: str | None, new_value: str | None
) -> None:
    """Record a change of a string configuration field."""
    logger.log(
        "settings",
        "update",
        key=key,
        old_value=old_value,
        new_value=new_value,
    )

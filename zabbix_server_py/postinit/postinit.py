"""Post-initialization routines translated from ``postinit.c``.

This module provides a minimal implementation of post start-up tasks.
It mirrors ``zbx_check_postinit_tasks()`` from
``src/zabbix_server/postinit/postinit.c`` and related helper
functions.  Each task is represented by a numeric constant taken from
``include/zbxtasks.h`` and is executed sequentially after the main
configuration is loaded.
"""

from __future__ import annotations

from typing import Callable, List

# Task type constants ---------------------------------------------------------

UPDATE_EVENTNAMES = 5  # ZBX_TM_TASK_UPDATE_EVENTNAMES
COPY_NESTED_HOST_PROTOTYPES = 10  # ZBX_TM_TASK_COPY_NESTED_HOST_PROTOTYPES


_tasks: List[int] = []
_log: List[str] = []


def reset() -> None:
    """Clear pending tasks and execution log."""
    _tasks.clear()
    _log.clear()


def add_task(task_type: int) -> None:
    """Queue a post-initialization task."""
    _tasks.append(task_type)


# individual task handlers ----------------------------------------------------

def update_event_names() -> None:
    """Placeholder for ``update_event_names`` in the C code."""
    _log.append("update_event_names")


def copy_nested_host_prototypes() -> None:
    """Placeholder for ``copy_nested_host_prototypes`` in the C code."""
    _log.append("copy_nested_host_prototypes")


_HANDLERS: dict[int, Callable[[], None]] = {
    UPDATE_EVENTNAMES: update_event_names,
    COPY_NESTED_HOST_PROTOTYPES: copy_nested_host_prototypes,
}


def run_postinit_tasks() -> List[str]:
    """Execute queued tasks in the order they were added.

    Returns the execution log for inspection by tests.
    """
    for t in list(_tasks):
        handler = _HANDLERS.get(t)
        if handler is not None:
            handler()
    _tasks.clear()
    return list(_log)


def get_log() -> List[str]:
    """Return a copy of the execution log."""
    return list(_log)

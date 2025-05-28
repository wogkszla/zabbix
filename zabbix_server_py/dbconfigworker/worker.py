from __future__ import annotations

"""Lightweight DB configuration worker."""

from dataclasses import dataclass, field
from typing import List

from .protocol import deserialize_ids


@dataclass
class DBConfigWorker:
    """Simplified worker processing host ID messages."""

    hostids: List[int] = field(default_factory=lambda: [0])

    def run(self, messages: List[bytes]) -> List[int]:
        """Process *messages* and return a sorted list of unique host IDs.

        This roughly corresponds to ``zbx_dbconfig_worker_thread`` which
        collects host IDs from IPC messages and then performs database
        synchronization.  The Python version only merges and returns the
        received IDs.
        """
        for data in messages:
            ids = deserialize_ids(data)
            self.hostids.extend(ids)

        unique_ids = sorted(set(self.hostids))
        if unique_ids and unique_ids[0] == 0:
            unique_ids = unique_ids[1:]

        self.hostids = [0]
        return unique_ids

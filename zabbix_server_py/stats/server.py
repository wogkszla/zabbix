"""Simplified internal statistics for the Python server."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class VCacheStats:
    """Value cache statistics."""

    total_size: int
    free_size: int
    hits: int
    misses: int
    mode: int = 0

    def as_dict(self) -> Dict[str, Any]:
        buffer_used = self.total_size - self.free_size
        return {
            "buffer": {
                "total": self.total_size,
                "free": self.free_size,
                "pfree": (self.free_size / self.total_size * 100) if self.total_size else 0,
                "used": buffer_used,
                "pused": (buffer_used / self.total_size * 100) if self.total_size else 0,
            },
            "cache": {
                "requests": self.hits + self.misses,
                "hits": self.hits,
                "misses": self.misses,
                "mode": self.mode,
            },
        }


@dataclass
class TCacheStats:
    """Trend cache statistics."""

    hits: int
    misses: int
    items_num: int
    requests_num: int

    def as_dict(self) -> Dict[str, Any]:
        total_hm = self.hits + self.misses
        total_ir = self.items_num + self.requests_num
        return {
            "hits": self.hits,
            "misses": self.misses,
            "all": total_hm,
            "phits": (self.hits / total_hm * 100) if total_hm else 0,
            "pmisses": (self.misses / total_hm * 100) if total_hm else 0,
            "items": self.items_num,
            "requests": self.requests_num,
            "pitems": (self.items_num / total_ir * 100) if total_ir else 0,
        }


@dataclass
class VpsStats:
    """Value pre-processing statistics."""

    written_num: int
    values_limit: int
    overcommit_limit: int
    overcommit: int
    capped: bool = False

    def as_dict(self) -> Dict[str, Any]:
        data = {
            "status": 1 if self.capped else 0,
            "written_total": self.written_num,
            "limit": self.values_limit,
        }
        if self.values_limit:
            avail = self.overcommit_limit - self.overcommit
            data["overcommit"] = {
                "limit": self.overcommit_limit,
                "available": avail,
                "pavailable": (avail / self.overcommit_limit * 100) if self.overcommit_limit else 0,
            }
        return data


@dataclass
class ServerStats:
    """Container for all server statistics."""

    lld_queue: int
    connector_queue: int
    triggers: int
    vcache: VCacheStats
    tcache: TCacheStats
    vps: VpsStats
    ha: Optional[Dict[str, Any]] = None
    proxy: Optional[Dict[str, Any]] = None

    def as_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "lld_queue": self.lld_queue,
            "connector_queue": self.connector_queue,
            "triggers": self.triggers,
            "vcache": self.vcache.as_dict(),
            "tcache": self.tcache.as_dict(),
            "vps": self.vps.as_dict(),
        }
        if self.ha is not None:
            data["ha"] = self.ha
        if self.proxy is not None:
            data["proxy"] = self.proxy
        return data

    def to_json(self) -> str:
        return json.dumps(self.as_dict())


def get_data_server(stats: ServerStats) -> str:
    """Return JSON encoded server statistics."""
    return stats.to_json()

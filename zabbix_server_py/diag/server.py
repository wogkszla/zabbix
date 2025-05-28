"""Simplified diagnostic section handling for the Python server."""
from __future__ import annotations

import json
from typing import Any, Dict

# Section constants mirroring include/zbxdiag.h
ZBX_DIAG_HISTORYCACHE = "historycache"
ZBX_DIAG_VALUECACHE = "valuecache"
ZBX_DIAG_PREPROCESSING = "preprocessing"
ZBX_DIAG_LLD = "lld"
ZBX_DIAG_ALERTING = "alerting"
ZBX_DIAG_LOCKS = "locks"
ZBX_DIAG_CONNECTOR = "connector"


_DEF_RESPONSE: Dict[str, Any] = {
    "stats": {},
    "top": {},
    "time": 0,
}


def _dummy_info(section: str, request: Dict[str, Any]) -> Dict[str, Any]:
    """Return a very small diagnostics payload."""
    info = {section: _DEF_RESPONSE.copy()}
    # attach request for visibility in tests
    if request:
        info[section]["request"] = request
    return info


def add_section_info(section: str, json_request: str | bytes | None) -> Dict[str, Any]:
    """Return diagnostic information for the requested section.

    Parameters
    ----------
    section : str
        Name of the diagnostics section to retrieve.
    json_request : str | bytes | None
        Optional JSON encoded request specifying stats/top fields.

    Returns
    -------
    Dict[str, Any]
        Simplified diagnostics information.

    Raises
    ------
    ValueError
        If *section* is not recognised.
    """
    req: Dict[str, Any] = {}
    if json_request:
        req = json.loads(json_request)

    if section == ZBX_DIAG_HISTORYCACHE:
        return _dummy_info(section, req)
    if section == ZBX_DIAG_VALUECACHE:
        return _dummy_info(section, req)
    if section == ZBX_DIAG_PREPROCESSING:
        return _dummy_info(section, req)
    if section == ZBX_DIAG_LLD:
        return _dummy_info(section, req)
    if section == ZBX_DIAG_ALERTING:
        return _dummy_info(section, req)
    if section == ZBX_DIAG_LOCKS:
        return _dummy_info(section, req)
    if section == ZBX_DIAG_CONNECTOR:
        return _dummy_info(section, req)

    raise ValueError(f"Unsupported diagnostics section: {section}")


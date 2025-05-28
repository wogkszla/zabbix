"""Simple serialization helpers from ``report_protocol.c``."""

from __future__ import annotations

import struct
from typing import Iterable, List, Tuple

__all__ = [
    "serialize_begin_report",
    "deserialize_begin_report",
    "serialize_response",
    "deserialize_response",
]


# ---------------------------------------------------------------------------
# Begin report message
# ---------------------------------------------------------------------------

def _pack_str(s: str) -> bytes:
    data = s.encode()
    return struct.pack("<I", len(data)) + data


def _unpack_str(data: bytes, offset: int) -> Tuple[str, int]:
    (length,) = struct.unpack_from("<I", data, offset)
    offset += 4
    s = data[offset : offset + length].decode()
    offset += length
    return s, offset


def serialize_begin_report(
    name: str, url: str, cookie: str, params: Iterable[Tuple[str, str]]
) -> bytes:
    """Serialize parameters as used in ``report_serialize_begin_report``."""
    items = list(params)
    payload = b"".join(_pack_str(p) + _pack_str(v) for p, v in items)
    header = b"".join((_pack_str(name), _pack_str(url), _pack_str(cookie), struct.pack("<I", len(items))))
    return header + payload


def deserialize_begin_report(data: bytes) -> Tuple[str, str, str, List[Tuple[str, str]]]:
    """Inverse of :func:`serialize_begin_report`."""
    offset = 0
    name, offset = _unpack_str(data, offset)
    url, offset = _unpack_str(data, offset)
    cookie, offset = _unpack_str(data, offset)
    (num_params,) = struct.unpack_from("<I", data, offset)
    offset += 4
    params: List[Tuple[str, str]] = []
    for _ in range(num_params):
        key, offset = _unpack_str(data, offset)
        val, offset = _unpack_str(data, offset)
        params.append((key, val))
    return name, url, cookie, params


# ---------------------------------------------------------------------------
# Response message
# ---------------------------------------------------------------------------


def serialize_response(status: int, error: str | None, results: Iterable[Tuple[int, str, str]]) -> bytes:
    """Serialize a report result message.

    Mirrors ``report_serialize_response`` but supports only the fields used in
    the tests.
    """
    if error is None:
        error = ""
    results_list = list(results)
    payload = struct.pack("<I", status) + _pack_str(error) + struct.pack("<I", len(results_list))
    for st, rec, info in results_list:
        payload += struct.pack("<I", st) + _pack_str(rec) + _pack_str(info)
    return payload


def deserialize_response(data: bytes) -> Tuple[int, str, List[Tuple[int, str, str]]]:
    """Decode bytes produced by :func:`serialize_response`."""
    offset = 0
    (status,) = struct.unpack_from("<I", data, offset)
    offset += 4
    err, offset = _unpack_str(data, offset)
    (count,) = struct.unpack_from("<I", data, offset)
    offset += 4
    results: List[Tuple[int, str, str]] = []
    for _ in range(count):
        (st,) = struct.unpack_from("<I", data, offset)
        offset += 4
        rec, offset = _unpack_str(data, offset)
        info, offset = _unpack_str(data, offset)
        results.append((st, rec, info))
    return status, err, results

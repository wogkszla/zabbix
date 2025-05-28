from __future__ import annotations

"""Utility functions for DB config worker messaging."""

import struct
from typing import Iterable, List


def serialize_ids(ids: Iterable[int]) -> bytes:
    """Serialize a sequence of host IDs.

    This mirrors ``zbx_dbconfig_worker_serialize_ids`` and encodes the
    IDs as a length-prefixed array of 64-bit little-endian integers.
    """
    id_list = list(ids)
    data_len = len(id_list) * 8
    payload = b"".join(struct.pack("<Q", i) for i in id_list)
    return struct.pack("<I", data_len) + payload


def deserialize_ids(data: bytes) -> List[int]:
    """Decode bytes produced by :func:`serialize_ids`.

    Equivalent to ``zbx_dbconfig_worker_deserialize_ids``.
    """
    if not data:
        return []
    (data_len,) = struct.unpack_from("<I", data, 0)
    ids: List[int] = []
    offset = 4
    end = 4 + data_len
    while offset < end:
        (val,) = struct.unpack_from("<Q", data, offset)
        ids.append(val)
        offset += 8
    return ids

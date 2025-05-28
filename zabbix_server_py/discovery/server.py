from __future__ import annotations

from dataclasses import dataclass
import sqlite3
from typing import List, Optional

# Constants mirroring include/zbxcommon.h
DOBJECT_STATUS_UP = 0
DOBJECT_STATUS_DOWN = 1
DOBJECT_STATUS_DISCOVER = 2
DOBJECT_STATUS_LOST = 3
DOBJECT_STATUS_FINALIZED = 4


@dataclass
class DHost:
    """Simplified representation of a discovered host."""

    dhostid: int = 0
    status: int = DOBJECT_STATUS_DOWN
    lastup: int = 0
    lastdown: int = 0


@dataclass
class DService:
    """Simplified representation of a discovered service."""

    dserviceid: int = 0
    dhostid: int = 0
    status: int = DOBJECT_STATUS_DOWN
    lastup: int = 0
    lastdown: int = 0
    value: str = ""


class DiscoveryServer:
    """Very small subset of the discovery logic using SQLite."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self.conn.row_factory = sqlite3.Row
        self._setup_schema()

    def _setup_schema(self) -> None:
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS dhosts (
                    dhostid INTEGER PRIMARY KEY AUTOINCREMENT,
                    druleid INTEGER NOT NULL,
                    status INTEGER NOT NULL,
                    lastup INTEGER NOT NULL,
                    lastdown INTEGER NOT NULL
                )
                """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS dservices (
                    dserviceid INTEGER PRIMARY KEY AUTOINCREMENT,
                    dhostid INTEGER NOT NULL,
                    dcheckid INTEGER NOT NULL,
                    ip TEXT NOT NULL,
                    dns TEXT NOT NULL,
                    port INTEGER NOT NULL,
                    status INTEGER NOT NULL,
                    lastup INTEGER NOT NULL,
                    lastdown INTEGER NOT NULL,
                    value TEXT NOT NULL
                )
                """
            )

    def close(self) -> None:
        self.conn.close()

    def find_host(self, druleid: int, ip: str) -> Optional[DHost]:
        row = self.conn.execute(
            """
            SELECT dh.dhostid, dh.status, dh.lastup, dh.lastdown
              FROM dhosts dh
              JOIN dservices ds ON ds.dhostid = dh.dhostid
             WHERE dh.druleid=? AND ds.ip=?
             ORDER BY dh.dhostid
             LIMIT 1
            """,
            (druleid, ip),
        ).fetchone()
        if not row:
            return None
        return DHost(
            dhostid=row["dhostid"],
            status=row["status"],
            lastup=row["lastup"],
            lastdown=row["lastdown"],
        )

    def _register_host(self, druleid: int) -> DHost:
        dhost = DHost()
        dhost.dhostid = self.conn.execute(
            "INSERT INTO dhosts (druleid, status, lastup, lastdown) VALUES (?, ?, 0, 0)",
            (druleid, DOBJECT_STATUS_DOWN),
        ).lastrowid
        return dhost

    def _register_service(
        self, dhostid: int, dcheckid: int, ip: str, dns: str, port: int
    ) -> DService:
        dservice = DService(dhostid=dhostid)
        dservice.dserviceid = self.conn.execute(
            """
            INSERT INTO dservices (dhostid, dcheckid, ip, dns, port, status, lastup, lastdown, value)
            VALUES (?, ?, ?, ?, ?, ?, 0, 0, '')
            """,
            (dhostid, dcheckid, ip, dns, port, DOBJECT_STATUS_DOWN),
        ).lastrowid
        return dservice

    def update_service(
        self,
        druleid: int,
        dcheckid: int,
        unique_dcheckid: int,
        dhost: DHost,
        ip: str,
        dns: str,
        port: int,
        status: int,
        value: str,
        now: int,
        dserviceids: List[int],
        add_event_cb=None,
    ) -> None:
        """Register host/service if necessary and update service status."""

        if dhost.dhostid == 0:
            found = self.find_host(druleid, ip)
            if found:
                dhost.dhostid = found.dhostid
                dhost.status = found.status
                dhost.lastup = found.lastup
                dhost.lastdown = found.lastdown
            elif status == DOBJECT_STATUS_UP:
                new_host = self._register_host(druleid)
                dhost.dhostid = new_host.dhostid
                dhost.status = new_host.status
                dhost.lastup = new_host.lastup
                dhost.lastdown = new_host.lastdown

        if dhost.dhostid == 0:
            # host not created when service is down
            return

        row = self.conn.execute(
            """
            SELECT dserviceid, status, lastup, lastdown, value
              FROM dservices
             WHERE dhostid=? AND dcheckid=? AND ip=? AND port=?
             LIMIT 1
            """,
            (dhost.dhostid, dcheckid, ip, port),
        ).fetchone()

        if row:
            dservice = DService(
                dserviceid=row["dserviceid"],
                dhostid=dhost.dhostid,
                status=row["status"],
                lastup=row["lastup"],
                lastdown=row["lastdown"],
                value=row["value"],
            )
        else:
            if status != DOBJECT_STATUS_UP:
                return
            dservice = self._register_service(dhost.dhostid, dcheckid, ip, dns, port)

        if status == DOBJECT_STATUS_UP:
            lastup = now
            lastdown = 0
        else:
            lastup = dservice.lastup
            lastdown = now

        with self.conn:
            self.conn.execute(
                """
                UPDATE dservices
                   SET status=?, lastup=?, lastdown=?, value=?
                 WHERE dserviceid=?
                """,
                (status, lastup, lastdown, value, dservice.dserviceid),
            )

        dserviceids.append(dservice.dserviceid)


def open(db: str | sqlite3.Connection | None = None) -> DiscoveryServer:
    """Create a discovery server handle."""
    if db is None:
        conn = sqlite3.connect(":memory:")
    elif isinstance(db, sqlite3.Connection):
        conn = db
    else:
        conn = sqlite3.connect(db)
    return DiscoveryServer(conn)


def close(server: DiscoveryServer) -> None:
    server.close()


def find_host(server: DiscoveryServer, druleid: int, ip: str) -> Optional[DHost]:
    return server.find_host(druleid, ip)


def update_service(
    server: DiscoveryServer,
    druleid: int,
    dcheckid: int,
    unique_dcheckid: int,
    dhost: DHost,
    ip: str,
    dns: str,
    port: int,
    status: int,
    value: str,
    now: int,
    dserviceids: List[int] | None = None,
    add_event_cb=None,
) -> List[int]:
    if dserviceids is None:
        dserviceids = []
    server.update_service(
        druleid,
        dcheckid,
        unique_dcheckid,
        dhost,
        ip,
        dns,
        port,
        status,
        value,
        now,
        dserviceids,
        add_event_cb,
    )
    return dserviceids

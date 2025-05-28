from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import sqlite3


@dataclass
class AutoRegHost:
    """Representation of an autoregistered host."""

    host: str
    ip: str
    dns: str
    port: int
    connection_type: int
    host_metadata: str
    flag: int
    now: int
    proxyid: Optional[int] = None
    autoreg_hostid: Optional[int] = None
    hostid: Optional[int] = None


class AutoRegServer:
    """Simplified autoregistration handler using SQLite."""

    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self.db_path = str(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._setup_schema()
        self._hosts: List[AutoRegHost] = []

    def _setup_schema(self) -> None:
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS autoreg_host (
                    autoreg_hostid INTEGER PRIMARY KEY AUTOINCREMENT,
                    proxyid INTEGER,
                    host TEXT NOT NULL,
                    listen_ip TEXT NOT NULL,
                    listen_port INTEGER NOT NULL,
                    listen_dns TEXT NOT NULL,
                    host_metadata TEXT NOT NULL,
                    flags INTEGER NOT NULL,
                    tls_accepted INTEGER NOT NULL DEFAULT 1
                )
                """
            )

    def close(self) -> None:
        self.conn.close()

    def prepare_host(
        self,
        host: str,
        ip: str,
        dns: str,
        port: int,
        connection_type: int,
        host_metadata: str,
        flag: int,
        now: int,
    ) -> None:
        """Prepare host information for flush."""
        # remove existing entry with the same host name if present
        self._hosts = [h for h in self._hosts if h.host != host]
        self._hosts.append(
            AutoRegHost(
                host=host,
                ip=ip,
                dns=dns,
                port=port,
                connection_type=connection_type,
                host_metadata=host_metadata,
                flag=flag,
                now=now,
            )
        )

    def flush_hosts(self, proxyid: Optional[int] = None) -> List[AutoRegHost]:
        """Insert or update prepared hosts in the database."""
        updated: List[AutoRegHost] = []

        for h in self._hosts:
            row = self.conn.execute(
                "SELECT autoreg_hostid FROM autoreg_host WHERE host=?",
                (h.host,),
            ).fetchone()
            if row:
                h.autoreg_hostid = row["autoreg_hostid"]
                with self.conn:
                    self.conn.execute(
                        """
                        UPDATE autoreg_host
                           SET listen_ip=?, listen_dns=?, listen_port=?,
                               host_metadata=?, flags=?, proxyid=?
                         WHERE autoreg_hostid=?
                        """,
                        (
                            h.ip,
                            h.dns,
                            h.port,
                            h.host_metadata,
                            h.flag,
                            proxyid,
                            h.autoreg_hostid,
                        ),
                    )
            else:
                with self.conn:
                    cur = self.conn.execute(
                        """
                        INSERT INTO autoreg_host (
                            proxyid, host, listen_ip, listen_port, listen_dns,
                            host_metadata, flags, tls_accepted
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                        """,
                        (
                            proxyid,
                            h.host,
                            h.ip,
                            h.port,
                            h.dns,
                            h.host_metadata,
                            h.flag,
                        ),
                    )
                    h.autoreg_hostid = cur.lastrowid
            updated.append(h)

        self._hosts.clear()
        return updated

    def update_host(
        self,
        host: str,
        ip: str,
        dns: str,
        port: int,
        connection_type: int,
        host_metadata: str,
        flag: int,
        now: int,
        proxyid: Optional[int] = None,
    ) -> AutoRegHost:
        """Register single host (prepare and flush)."""
        self.prepare_host(host, ip, dns, port, connection_type, host_metadata, flag, now)
        hosts = self.flush_hosts(proxyid=proxyid)
        return hosts[0]

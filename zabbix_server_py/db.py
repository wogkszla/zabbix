"""Database access layer.

This module provides a simple wrapper around a MySQL connection. It is
inspired by functions like zbx_db_connect() found in
src/libs/zbxdb/dbconn.c.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

try:
    import pymysql
except Exception:  # pragma: no cover - pymysql not installed
    pymysql = None  # type: ignore

@dataclass
class Config:
    host: str = "localhost"
    port: int = 3306
    user: str = "zabbix"
    password: str = "zabbix"
    database: str = "zabbix"

    @classmethod
    def from_file(cls, path: str) -> "Config":
        """Load configuration from file.

        This is a placeholder matching zbx_load_config() behavior.
        """
        # TODO: parse actual configuration file
        return cls()

class Database:
    """Represent a connection to the database."""
    def __init__(self, config: Config) -> None:
        self.config = config
        self.conn: Optional["pymysql.connections.Connection"] = None

    def connect(self) -> None:
        """Connect to MySQL database.

        Equivalent to calling zbx_db_connect() in the C code.
        """
        if pymysql is None:
            raise RuntimeError("pymysql not available")

        self.conn = pymysql.connect(
            host=self.config.host,
            port=self.config.port,
            user=self.config.user,
            password=self.config.password,
            database=self.config.database,
        )

    def close(self) -> None:
        if self.conn is not None:
            self.conn.close()
            self.conn = None

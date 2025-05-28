import os
import sys
from unittest import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from zabbix_server_py import db


def test_db_connect_calls_pymysql_connect():
    cfg = db.Config()
    database = db.Database(cfg)
    with mock.patch("zabbix_server_py.db.pymysql") as pymysql:
        database.connect()
        pymysql.connect.assert_called_with(
            host=cfg.host,
            port=cfg.port,
            user=cfg.user,
            password=cfg.password,
            database=cfg.database,
        )

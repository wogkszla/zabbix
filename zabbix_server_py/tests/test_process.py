import os
import sys
from unittest import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from zabbix_server_py import process


def test_start_master_spawns_process():
    with mock.patch("zabbix_server_py.process.Process") as proc:
        instance = proc.return_value
        process.start_master()
        proc.assert_called()
        instance.start.assert_called()
        instance.join.assert_called()

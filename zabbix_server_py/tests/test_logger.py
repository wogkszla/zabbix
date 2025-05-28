import os
import sys
from unittest import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from zabbix_server_py import logger


def test_setup_logging_stream(monkeypatch):
    with mock.patch("logging.basicConfig") as basic:
        logger.setup_logging()
        basic.assert_called()

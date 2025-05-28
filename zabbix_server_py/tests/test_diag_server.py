from zabbix_server_py.diag.server import add_section_info
import pytest


def test_unknown_section_raises():
    with pytest.raises(ValueError):
        add_section_info("unknown", "{}")


import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from zabbix_server_py import main


def test_parse_args():
    args = main.parse_args(["-c", "test.conf", "-T"])
    assert args.config == "test.conf"
    assert args.test_config is True


def test_main_test_config(capsys):
    main.main(["-T"])
    captured = capsys.readouterr()
    assert "Validation successful" in captured.out

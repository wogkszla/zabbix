from zabbix_server_py.main import parse_args, main


def test_parse_args_defaults():
    args = parse_args([])
    assert args.config == "/etc/zabbix/zabbix_server.conf"
    assert args.test_config is False
    assert args.foreground is False


def test_parse_args_all_options():
    args = parse_args(["-c", "my.conf", "-R", "reload", "-f"])
    assert args.config == "my.conf"
    assert args.runtime_control == "reload"
    assert args.foreground is True


def test_test_config_mode(capsys):
    exit_code = main(["-T", "-c", "sample.conf"])
    captured = capsys.readouterr()
    assert "Validation successful" in captured.out
    assert exit_code == 0


def test_version_mode(capsys):
    exit_code = main(["-V"])
    captured = capsys.readouterr()
    assert "Zabbix Server" in captured.out
    assert exit_code == 0

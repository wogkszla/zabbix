from zabbix_server_py.main import parse_args, main


def test_parse_args_defaults():
    args = parse_args([])
    assert args.config is None
    assert args.test_config is False
    assert args.foreground is False


def test_test_config_mode(capsys):
    exit_code = main(["-T", "-c", "sample.conf"])
    captured = capsys.readouterr()
    assert "Validation successful" in captured.out
    assert exit_code == 0

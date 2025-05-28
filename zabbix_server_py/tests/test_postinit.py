from zabbix_server_py.postinit import (
    UPDATE_EVENTNAMES,
    COPY_NESTED_HOST_PROTOTYPES,
    add_task,
    run_postinit_tasks,
    reset,
    get_log,
)
from zabbix_server_py.main import main


def setup_function(_func):
    reset()


def test_tasks_run_in_order():
    add_task(UPDATE_EVENTNAMES)
    add_task(COPY_NESTED_HOST_PROTOTYPES)
    log = run_postinit_tasks()
    assert log == ["update_event_names", "copy_nested_host_prototypes"]


def test_postinit_called_after_config(monkeypatch):
    calls = []

    def fake_load(path):
        calls.append("config")

    def fake_run():
        calls.append("postinit")

    monkeypatch.setattr("zabbix_server_py.main.load_config", fake_load)
    monkeypatch.setattr("zabbix_server_py.main.run_postinit_tasks", fake_run)

    main(["-c", "conf"])

    assert calls == ["config", "postinit"]

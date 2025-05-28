from zabbix_server_py.audit import (
    AuditLogger,
    proxy_config_reload,
    settings_create_entry,
    settings_update_field_str,
)


def test_proxy_config_reload():
    logger = AuditLogger()
    proxy_config_reload(logger, 42, "proxy1")
    assert len(logger.entries) == 1
    entry = logger.entries[0]
    assert entry.resource == "proxy"
    assert entry.action == "config_reload"
    assert entry.data["id"] == 42
    assert entry.data["name"] == "proxy1"


def test_settings_audit():
    logger = AuditLogger()
    settings_create_entry(logger, "update")
    settings_update_field_str(logger, "log_level", "INFO", "DEBUG")
    assert len(logger.entries) == 2
    create_entry, update_entry = logger.entries
    assert create_entry.resource == "settings"
    assert create_entry.action == "update"
    assert update_entry.data["key"] == "log_level"
    assert update_entry.data["old_value"] == "INFO"
    assert update_entry.data["new_value"] == "DEBUG"

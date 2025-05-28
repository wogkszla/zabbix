from __future__ import annotations

import json
from typing import Any, List, Tuple

from zabbix_server_py.ha import (
    HAManager,
    zbx_ha_get_nodes,
    zbx_ha_get_failover_delay,
    zbx_ha_set_failover_delay,
    zbx_ha_remove_node,
)

# command option strings -------------------------------------------------------
CMD_CONFIG_CACHE_RELOAD = "config_cache_reload"
CMD_SERVICE_CACHE_RELOAD = "service_cache_reload"
CMD_SECRETS_RELOAD = "secrets_reload"
CMD_TRIGGER_HOUSEKEEPER_EXECUTE = "trigger_housekeeper_execute"
CMD_DIAGINFO = "diaginfo"
CMD_HA_STATUS = "ha_status"
CMD_HA_REMOVE_NODE = "ha_remove_node"
CMD_HA_SET_FAILOVER_DELAY = "ha_set_failover_delay"
CMD_PROXY_CONFIG_CACHE_RELOAD = "proxy_config_cache_reload"
CMD_PROXYPOLLER_PROCESS = "proxypoller_process"
CMD_LOG_LEVEL_INCREASE = "log_level_increase"
CMD_LOG_LEVEL_DECREASE = "log_level_decrease"


class RTCServer:
    """Simplified runtime control server."""

    def __init__(self, ha_manager: HAManager | None = None) -> None:
        self.ha_manager = ha_manager or HAManager()
        self.actions: list[Tuple[str, Any]] = []

    # basic notifications ---------------------------------------------------
    def _notify(self, action: str, data: Any | None = None) -> None:
        self.actions.append((action, data))

    # runtime actions -------------------------------------------------------
    def config_cache_reload(self) -> None:
        self._notify(CMD_CONFIG_CACHE_RELOAD)

    def service_cache_reload(self) -> None:
        self._notify(CMD_SERVICE_CACHE_RELOAD)

    def secrets_reload(self) -> None:
        self._notify(CMD_SECRETS_RELOAD)

    def trigger_housekeeper_execute(self) -> None:
        self._notify(CMD_TRIGGER_HOUSEKEEPER_EXECUTE)

    def proxypoller_process(self) -> None:
        self._notify(CMD_PROXYPOLLER_PROCESS)

    def proxy_config_cache_reload(self, names: List[str] | None = None) -> None:
        self._notify(CMD_PROXY_CONFIG_CACHE_RELOAD, names or [])

    def log_level_increase(self) -> Any:
        return self.ha_manager.send(HAManager.CMD_LOGLEVEL_INCREASE)

    def log_level_decrease(self) -> Any:
        return self.ha_manager.send(HAManager.CMD_LOGLEVEL_DECREASE)

    def ha_status(self) -> Any:
        return self.ha_manager.send(HAManager.CMD_STATUS)

    def ha_remove_node(self, node: str) -> Any:
        return zbx_ha_remove_node(self.ha_manager, node)

    def ha_set_failover_delay(self, delay: int) -> Any:
        return zbx_ha_set_failover_delay(self.ha_manager, delay)

    def diaginfo(self, json_data: str) -> Any:
        self._notify(CMD_DIAGINFO, json.loads(json_data))
        return {}

    # ------------------------------------------------------------------
    def parse_option(self, option: str) -> Tuple[str, Any | None]:
        if option == CMD_CONFIG_CACHE_RELOAD:
            return CMD_CONFIG_CACHE_RELOAD, None
        if option == CMD_SERVICE_CACHE_RELOAD:
            return CMD_SERVICE_CACHE_RELOAD, None
        if option == CMD_SECRETS_RELOAD:
            return CMD_SECRETS_RELOAD, None
        if option == CMD_TRIGGER_HOUSEKEEPER_EXECUTE:
            return CMD_TRIGGER_HOUSEKEEPER_EXECUTE, None
        if option == CMD_PROXYPOLLER_PROCESS:
            return CMD_PROXYPOLLER_PROCESS, None
        if option == CMD_HA_STATUS:
            return CMD_HA_STATUS, None
        if option == CMD_LOG_LEVEL_INCREASE:
            return CMD_LOG_LEVEL_INCREASE, None
        if option == CMD_LOG_LEVEL_DECREASE:
            return CMD_LOG_LEVEL_DECREASE, None

        if option.startswith(CMD_HA_REMOVE_NODE):
            param = option[len(CMD_HA_REMOVE_NODE):]
            if param.startswith("="):
                node = param[1:]
                if node:
                    return CMD_HA_REMOVE_NODE, node
                raise ValueError("missing node parameter")
            raise ValueError("missing node parameter")

        if option.startswith(CMD_HA_SET_FAILOVER_DELAY):
            param = option[len(CMD_HA_SET_FAILOVER_DELAY):]
            if param.startswith("="):
                try:
                    delay = int(param[1:])
                except ValueError as exc:
                    raise ValueError("invalid failover delay") from exc
                return CMD_HA_SET_FAILOVER_DELAY, delay
            raise ValueError("missing failover delay parameter")

        if option.startswith(CMD_PROXY_CONFIG_CACHE_RELOAD):
            param = option[len(CMD_PROXY_CONFIG_CACHE_RELOAD):]
            if param == "":
                return CMD_PROXY_CONFIG_CACHE_RELOAD, None
            if param.startswith("="):
                names_str = param[1:]
                if names_str == "":
                    raise ValueError("missing proxy names")
                names = [n for n in names_str.split(',') if n]
                return CMD_PROXY_CONFIG_CACHE_RELOAD, names
            raise ValueError("invalid proxy_config_cache_reload parameter")

        if option.startswith(CMD_DIAGINFO):
            param = option[len(CMD_DIAGINFO):]
            if param.startswith("="):
                return CMD_DIAGINFO, param[1:]
            raise ValueError("missing diaginfo parameter")

        raise ValueError(f"unknown option: {option}")

    def dispatch(self, code: str, data: Any | None) -> Any:
        if code == CMD_CONFIG_CACHE_RELOAD:
            return self.config_cache_reload()
        if code == CMD_SERVICE_CACHE_RELOAD:
            return self.service_cache_reload()
        if code == CMD_SECRETS_RELOAD:
            return self.secrets_reload()
        if code == CMD_TRIGGER_HOUSEKEEPER_EXECUTE:
            return self.trigger_housekeeper_execute()
        if code == CMD_PROXYPOLLER_PROCESS:
            return self.proxypoller_process()
        if code == CMD_PROXY_CONFIG_CACHE_RELOAD:
            return self.proxy_config_cache_reload(data)
        if code == CMD_HA_STATUS:
            return self.ha_status()
        if code == CMD_HA_REMOVE_NODE:
            return self.ha_remove_node(str(data))
        if code == CMD_HA_SET_FAILOVER_DELAY:
            return self.ha_set_failover_delay(int(data))
        if code == CMD_DIAGINFO:
            return self.diaginfo(str(data))
        if code == CMD_LOG_LEVEL_INCREASE:
            return self.log_level_increase()
        if code == CMD_LOG_LEVEL_DECREASE:
            return self.log_level_decrease()
        raise ValueError(f"unsupported code: {code}")

    def process(self, option: str) -> Any:
        code, data = self.parse_option(option)
        return self.dispatch(code, data)

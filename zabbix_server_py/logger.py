"""Logging helpers.

This module takes inspiration from zbx_open_log() and related
functions in src/libs/zbxlog/log.c.
"""
from __future__ import annotations
import logging

LOGGER_NAME = "zabbix_server"


def setup_logging(level: int = logging.INFO, filename: str | None = None) -> None:
    """Configure global logging.

    Parameters correspond loosely to log level and file options used in
    the original C implementation.
    """
    handlers = [logging.StreamHandler()]
    if filename is not None:
        handlers.append(logging.FileHandler(filename))

    logging.basicConfig(level=level, handlers=handlers, format="%(asctime)s %(levelname)s: %(message)s")

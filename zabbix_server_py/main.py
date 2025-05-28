"""CLI skeleton for Python rewrite of Zabbix server."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import load_config

DEFAULT_CONFIG = Path("/etc/zabbix/zabbix_server.conf")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="zabbix_server")
    parser.add_argument(
        "-c",
        "--config",
        default=str(DEFAULT_CONFIG),
        help="path to config file",
    )
    parser.add_argument("-R", "--runtime-control", help="runtime control command")
    parser.add_argument("-T", "--test-config", action="store_true", help="test configuration and exit")
    parser.add_argument("-f", "--foreground", action="store_true", help="run in foreground")
    parser.add_argument("-V", "--version", action="store_true", help="display version and exit")
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = build_parser()
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.version:
        print("Zabbix Server (Python rewrite)")
        return 0

    config_path = Path(args.config)

    # load configuration (placeholder)
    load_config(config_path)

    if args.test_config:
        print("Validation successful")
        return 0

    # TODO: initialization logic goes here
    print("Starting server...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

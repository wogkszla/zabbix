# Python Refactoring Steps

This document outlines the initial steps to port the Zabbix server from C to Python.

## Environment
- Ubuntu 22.04
- Python 3.12.9 (or system Python 3.11+)
- MySQL 8.0+

Install dependencies and create a virtual environment:

```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev mysql-server
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the CLI

The Python entry point lives in `zabbix_server_py/main.py`.
Run with:

```bash
python -m zabbix_server_py.main -h
```

`-T` will run in test mode and exit after printing "Validation successful".

## Tests

Tests use `pytest` and are located under `zabbix_server_py/tests/`.
Run them with:

```bash
pytest
```

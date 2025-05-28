# Python 환경 및 프로젝트 골격 구성 가이드

이 문서는 Zabbix 서버를 Python 3.12.9 기반으로 단계적으로 리팩토링하기 위한 개발 환경 준비와 초기 프로젝트 구조 생성 방법을 안내합니다. Ubuntu 22.04를 기준으로 작성되었습니다.

## 1. 필수 패키지 설치

```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev mysql-server
```

`mysql-server` 패키지는 테스트용 MySQL 8.0 이상 버전을 설치합니다. 시스템에 이미 MySQL이 설치되어 있다면 생략할 수 있습니다.

## 2. 가상환경 준비

```bash
python3.12 -m venv venv
source venv/bin/activate
```

가상환경을 활성화한 뒤 아래와 같이 필요한 파이썬 모듈을 설치합니다.

```bash
pip install mysqlclient pytest
```

설치한 패키지는 `requirements.txt` 파일로 관리합니다.

```bash
cat > requirements.txt <<'REQ'
mysqlclient>=2.2.0
pytest>=7.0
REQ
```

## 3. 프로젝트 디렉터리 구조

초기 구조 예시는 다음과 같습니다.

```
zabbix_server_py/
├── requirements.txt
├── README.md
├── zabbix_server/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   └── modules/
├── tests/
│   └── test_main.py
```

- `zabbix_server/`에는 서버 동작에 필요한 파이썬 모듈을 배치합니다.
- `tests/` 폴더는 `pytest` 기반 단위 테스트를 둡니다.

## 4. 기본 `main.py` 작성 예시

```python
# zabbix_server/main.py
import argparse
import sys


def parse_args(args=None):
    parser = argparse.ArgumentParser(prog="zabbix_server")
    parser.add_argument("-c", "--config", default="/etc/zabbix/zabbix_server.conf")
    parser.add_argument("-R", "--runtime-control")
    parser.add_argument("-T", "--test-config", action="store_true")
    parser.add_argument("-f", "--foreground", action="store_true")
    parser.add_argument("-V", "--version", action="store_true")
    return parser.parse_args(args)


def main(argv=None):
    args = parse_args(argv)

    if args.version:
        print("Zabbix Server (Python rewrite)")
        return

    if args.test_config:
        print("Validation successful")
        return

    print(f"Using config: {args.config}")
    # TODO: 설정 파일 로딩 및 모듈 초기화


if __name__ == "__main__":
    main()
```

## 5. 간단한 테스트 코드 예시

```python
# tests/test_main.py
from zabbix_server.main import parse_args


def test_default_config():
    args = parse_args([])
    assert args.config == "/etc/zabbix/zabbix_server.conf"
```

`pytest`를 실행해 테스트가 통과하는지 확인합니다.

```bash
pytest -q
```

이 가이드를 따라 환경을 준비하면, 기존 C 코드를 Python으로 옮기는 작업을 단계적으로 진행할 수 있습니다.

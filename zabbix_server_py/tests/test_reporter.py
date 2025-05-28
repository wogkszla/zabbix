from datetime import datetime

from zabbix_server_py.reporter import (
    time_to_urlfield,
    get_report_range,
    get_report_name,
    serialize_begin_report,
    deserialize_begin_report,
    serialize_response,
    deserialize_response,
    fetch_report,
)


def test_time_to_urlfield():
    dt = datetime(2024, 1, 2, 3, 4, 5)
    assert time_to_urlfield(dt) == "2024-01-02%2003%3A04%3A05"


def test_get_report_name():
    ts = int(datetime(2024, 1, 2, 3, 0).timestamp())
    assert get_report_name("Report /name", ts) == "Report__name_2024-01-02_03-00.pdf"


def test_get_report_range_week():
    ts = int(datetime(2024, 1, 5, 12, 0).timestamp())
    start, end = get_report_range(ts, 1)
    assert start.weekday() == 0  # Monday
    assert (end - start).days == 7


def test_begin_report_roundtrip():
    data = serialize_begin_report("r", "u", "c", [("p", "v")])
    name, url, cookie, params = deserialize_begin_report(data)
    assert name == "r" and url == "u" and cookie == "c"
    assert params == [("p", "v")]


def test_response_roundtrip():
    res = [(1, "a", "b"), (0, "x", "y")]
    data = serialize_response(0, "", res)
    status, error, out = deserialize_response(data)
    assert status == 0 and error == "" and out == res


def test_fetch_report():
    data = fetch_report("http://x", "sid", webservice_url="ws")
    assert data.startswith(b"%PDF")
    assert b"URL:http://x" in data
    assert b"COOKIE:sid" in data


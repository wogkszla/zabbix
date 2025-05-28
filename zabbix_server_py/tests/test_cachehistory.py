from zabbix_server_py.cachehistory.cache import HistoryCache


def test_store_and_retrieve():
    cache = HistoryCache()
    cache.add(1, 100, timestamp=1)
    cache.add(1, 200, timestamp=2)

    assert cache.get_last(1) == 200
    assert cache.get_history(1) == [(1, 100), (2, 200)]

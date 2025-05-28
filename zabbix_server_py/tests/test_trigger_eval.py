from zabbix_server_py.cachehistory.cache import HistoryCache
from zabbix_server_py.cachehistory.trigger import Trigger


def test_trigger_evaluation():
    cache = HistoryCache()
    cache.add(1, 20)

    trig = Trigger(1, "cache.get_last(1) > 10")
    assert trig.evaluate(cache) is True

    trig = Trigger(2, "cache.get_last(1) < 10")
    assert trig.evaluate(cache) is False

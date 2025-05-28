from threading import Thread
import time

from zabbix_server_py.preproc import PreprocServer, PreprocValueOpt, FLAG_DISCOVERY_RULE, PP_VALUE_OPT_META
from zabbix_server_py.cachehistory.cache import HistoryCache


def test_preproc_flushes_history():
    cache = HistoryCache()
    srv = PreprocServer(cache)
    t = Thread(target=srv.run, daemon=True)
    t.start()

    srv.submit(1, 123, ts=1)

    for _ in range(20):
        if cache.get_last(1) == 123:
            break
        time.sleep(0.05)

    srv.stop()
    t.join(timeout=1)
    assert cache.get_last(1) == 123


def test_discovery_rule_goes_to_lld_queue():
    srv = PreprocServer()
    t = Thread(target=srv.run, daemon=True)
    t.start()

    srv.submit(2, "data", flags=FLAG_DISCOVERY_RULE, ts=1)

    for _ in range(20):
        if srv.lld_queue:
            break
        time.sleep(0.05)

    srv.stop()
    t.join(timeout=1)

    assert srv.lld_queue[0]["itemid"] == 2
    assert srv.lld_queue[0]["value"] == "data"


def test_prepare_value_checks_none():
    cache = HistoryCache()
    srv = PreprocServer(cache)
    t = Thread(target=srv.run, daemon=True)
    t.start()

    srv.submit(3, None, ts=1)
    # also send one with meta so it is accepted
    srv.submit(4, None, flags=FLAG_DISCOVERY_RULE, value_opt=PreprocValueOpt(flags=PP_VALUE_OPT_META), ts=1)

    time.sleep(0.2)
    srv.stop()
    t.join(timeout=1)

    assert cache.get_last(3) is None
    assert srv.lld_queue and srv.lld_queue[0]["itemid"] == 4

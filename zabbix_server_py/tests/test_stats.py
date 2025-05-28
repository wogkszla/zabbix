import json

from zabbix_server_py.stats import (
    VCacheStats,
    TCacheStats,
    VpsStats,
    ServerStats,
    get_data_server,
)


def test_server_stats_json():
    vcache = VCacheStats(total_size=100, free_size=40, hits=10, misses=5, mode=1)
    tcache = TCacheStats(hits=3, misses=1, items_num=2, requests_num=6)
    vps = VpsStats(written_num=8, values_limit=10, overcommit_limit=5, overcommit=2, capped=True)

    stats = ServerStats(
        lld_queue=7,
        connector_queue=2,
        triggers=4,
        vcache=vcache,
        tcache=tcache,
        vps=vps,
        ha={"status": "ok"},
        proxy={"num": 1},
    )

    data = json.loads(get_data_server(stats))

    assert data["lld_queue"] == 7
    assert data["connector_queue"] == 2
    assert data["triggers"] == 4

    buf = data["vcache"]["buffer"]
    assert buf["total"] == 100
    assert buf["free"] == 40
    assert round(buf["pfree"], 2) == 40.0
    assert buf["used"] == 60
    assert round(buf["pused"], 2) == 60.0

    tcache_json = data["tcache"]
    assert tcache_json["hits"] == 3
    assert tcache_json["misses"] == 1
    assert round(tcache_json["phits"], 2) == 75.0
    assert round(tcache_json["pmisses"], 2) == 25.0

    vps_json = data["vps"]
    assert vps_json["status"] == 1
    assert vps_json["written_total"] == 8
    assert vps_json["limit"] == 10
    assert vps_json["overcommit"]["limit"] == 5
    assert vps_json["overcommit"]["available"] == 3

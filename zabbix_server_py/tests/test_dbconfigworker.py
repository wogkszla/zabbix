from zabbix_server_py.dbconfigworker.protocol import serialize_ids, deserialize_ids
from zabbix_server_py.dbconfigworker.worker import DBConfigWorker


def test_serialize_roundtrip():
    ids = [1, 2, 3]
    data = serialize_ids(ids)
    assert deserialize_ids(data) == ids


def test_worker_merges_ids():
    worker = DBConfigWorker()
    msg1 = serialize_ids([3, 1])
    msg2 = serialize_ids([2, 3])

    result = worker.run([msg1, msg2])

    assert result == [1, 2, 3]
    # second run without new messages should return empty list
    assert worker.run([]) == []

from zabbix_server_py.discovery import server as ds


def test_register_service_creates_host_and_service():
    srv = ds.open()
    host = ds.DHost()
    ids = ds.update_service(
        srv,
        druleid=1,
        dcheckid=1,
        unique_dcheckid=1,
        dhost=host,
        ip="192.0.2.1",
        dns="h1",
        port=80,
        status=ds.DOBJECT_STATUS_UP,
        value="ok",
        now=1,
    )
    assert host.dhostid != 0
    assert ids
    row = srv.conn.execute(
        "SELECT status,lastup FROM dservices WHERE dserviceid=?",
        (ids[0],),
    ).fetchone()
    assert row["status"] == ds.DOBJECT_STATUS_UP
    assert row["lastup"] == 1
    ds.close(srv)


def test_host_not_created_when_service_down():
    srv = ds.open()
    host = ds.DHost()
    ids = ds.update_service(
        srv,
        druleid=1,
        dcheckid=2,
        unique_dcheckid=2,
        dhost=host,
        ip="192.0.2.5",
        dns="h2",
        port=80,
        status=ds.DOBJECT_STATUS_DOWN,
        value="",
        now=2,
    )
    assert host.dhostid == 0
    assert ids == []
    ds.close(srv)


def test_find_host():
    srv = ds.open()
    host = ds.DHost()
    ds.update_service(
        srv,
        druleid=3,
        dcheckid=1,
        unique_dcheckid=1,
        dhost=host,
        ip="192.0.2.9",
        dns="h3",
        port=80,
        status=ds.DOBJECT_STATUS_UP,
        value="",
        now=3,
    )
    found = ds.find_host(srv, 3, "192.0.2.9")
    assert found is not None
    assert found.dhostid == host.dhostid
    ds.close(srv)

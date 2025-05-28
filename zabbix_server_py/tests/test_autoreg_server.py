from zabbix_server_py.autoreg.autoreg_server import AutoRegServer


def test_register_new_host(tmp_path):
    db_file = tmp_path / "autoreg.db"
    server = AutoRegServer(db_file)
    host = server.update_host(
        host="agent1",
        ip="192.0.2.1",
        dns="agent1.example",
        port=10050,
        connection_type=0,
        host_metadata="",
        flag=0,
        now=0,
    )
    row = server.conn.execute("SELECT host, listen_ip FROM autoreg_host WHERE autoreg_hostid=?", (host.autoreg_hostid,)).fetchone()
    assert row["host"] == "agent1"
    assert row["listen_ip"] == "192.0.2.1"
    server.close()


def test_register_existing_host_updates(tmp_path):
    db_file = tmp_path / "autoreg.db"
    server = AutoRegServer(db_file)
    server.update_host(
        host="agent2",
        ip="192.0.2.2",
        dns="agent2.example",
        port=10050,
        connection_type=0,
        host_metadata="",
        flag=0,
        now=0,
    )
    server.update_host(
        host="agent2",
        ip="192.0.2.99",
        dns="agent2.example",
        port=10051,
        connection_type=0,
        host_metadata="",
        flag=1,
        now=0,
    )
    row = server.conn.execute("SELECT listen_ip, listen_port, flags FROM autoreg_host WHERE host='agent2'").fetchone()
    assert row["listen_ip"] == "192.0.2.99"
    assert row["listen_port"] == 10051
    assert row["flags"] == 1
    server.close()


def test_prepare_and_flush_multiple_hosts(tmp_path):
    db_file = tmp_path / "autoreg.db"
    server = AutoRegServer(db_file)
    server.prepare_host("h1", "10.0.0.1", "h1", 10050, 0, "", 0, 0)
    server.prepare_host("h2", "10.0.0.2", "h2", 10050, 0, "", 0, 0)
    hosts = server.flush_hosts()
    assert len(hosts) == 2
    rows = server.conn.execute("SELECT COUNT(*) as c FROM autoreg_host").fetchone()
    assert rows["c"] == 2
    server.close()


from __future__ import annotations

from threading import Thread
import socket
import time

from zabbix_server_py.proxypoller.poller import Proxy, ProxyPoller


class FakeProxyServer:
    def __init__(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("127.0.0.1", 0))
        self.addr, self.port = self.sock.getsockname()
        self.running = False
        self.thread: Thread | None = None
        self.connections = 0

    def start(self) -> None:
        self.sock.listen()
        self.running = True
        self.thread = Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self) -> None:
        while self.running:
            try:
                conn, _ = self.sock.accept()
            except OSError:
                break
            with conn:
                self.connections += 1
                try:
                    data = conn.recv(1024)
                    if data:
                        conn.sendall(b"OK")
                finally:
                    pass

    def stop(self) -> None:
        self.running = False
        try:
            socket.create_connection((self.addr, self.port), timeout=0.1).close()
        except OSError:
            pass
        if self.thread is not None:
            self.thread.join(timeout=1)
        self.sock.close()


def test_proxy_poller_receives_data():
    server = FakeProxyServer()
    server.start()
    proxy = Proxy("p1", addr=server.addr, port=server.port)
    poller = ProxyPoller([proxy], frequency=0.1, timeout=0.5)
    t = Thread(target=poller.run, daemon=True)
    t.start()

    for _ in range(20):
        if proxy.last_response == "OK":
            break
        time.sleep(0.1)

    poller.stop()
    t.join(timeout=1)
    server.stop()

    assert proxy.last_response == "OK"
    assert proxy.lastaccess > 0


def test_proxy_poller_handles_connection_error():
    # allocate unused port
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()

    proxy = Proxy("p1", addr="127.0.0.1", port=port)
    poller = ProxyPoller([proxy], frequency=0.1, timeout=0.1)
    t = Thread(target=poller.run, daemon=True)
    t.start()

    time.sleep(0.3)

    poller.stop()
    t.join(timeout=1)

    assert proxy.last_response is None
    assert proxy.lastaccess == 0

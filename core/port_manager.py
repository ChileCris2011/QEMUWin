# core/port_manager.py

import socket
import threading


class PortManager:

    def __init__(self, start_qmp=4000, start_vnc=5900):
        self._lock = threading.Lock()
        self._used_ports = set()
        self._start_qmp = start_qmp
        self._start_vnc = start_vnc

    # ------------------------
    # INTERNAL CHECK
    # ------------------------

    def _is_port_free(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return True
            except OSError:
                return False

    def _find_free_port(self, start):
        port = start
        while True:
            if port not in self._used_ports and self._is_port_free(port):
                return port
            port += 1

    # ------------------------
    # PUBLIC API
    # ------------------------

    def allocate_qmp(self):
        with self._lock:
            port = self._find_free_port(self._start_qmp)
            self._used_ports.add(port)
            return port

    def allocate_vnc(self):
        with self._lock:
            port = self._find_free_port(self._start_vnc)
            self._used_ports.add(port)
            return port

    def release(self, port):
        with self._lock:
            self._used_ports.discard(port)
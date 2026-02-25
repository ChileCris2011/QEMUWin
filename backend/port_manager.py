import socket


class QMPPortManager:
    def __init__(self, start_port=4444):
        self.start_port = start_port
        self.used_ports = set()

    def _is_port_free(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("127.0.0.1", port)) != 0

    def get_free_port(self):
        port = self.start_port
        while True:
            if port not in self.used_ports and self._is_port_free(port):
                self.used_ports.add(port)
                return port
            port += 1

    def release_port(self, port):
        if port in self.used_ports:
            self.used_ports.remove(port)
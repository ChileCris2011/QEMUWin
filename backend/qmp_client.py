import socket
import json
import threading

class QMPClient:
    def __init__(self, host="127.0.0.1", port=4444):
        self.host = host
        self.port = port
        self.sock = None
        self.lock = threading.Lock()

    def connect(self):
        self.sock = socket.create_connection((self.host, self.port))
        self._recv()
        self.execute("qmp_capabilities")

    def execute(self, command, arguments=None):
        with self.lock:
            payload = {"execute": command}
            if arguments:
                payload["arguments"] = arguments

            self.sock.sendall((json.dumps(payload) + "\r\n").encode())
            return self._recv()

    def _recv(self):
        data = self.sock.recv(4096)
        return json.loads(data.decode())

    def shutdown(self):
        return self.execute("system_powerdown")

    def quit(self):
        return self.execute("quit")

    def close(self):
        if self.sock:
            self.sock.close()
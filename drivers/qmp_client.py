import socket
import json
import threading
import time

class QMPClient:

    def __init__(self, host="127.0.0.1", port=4444, event_bus=None):
        self.host = host
        self.port = port
        self.socket = None
        self._listener_thread = None
        self._running = False
        self.event_bus = event_bus

    # ------------------------
    # CONNECT
    # ------------------------

    def connect(self, retries=10):
        for _ in range(retries):
            try:
                self.socket = socket.create_connection((self.host, self.port))
                break
            except ConnectionRefusedError:
                time.sleep(0.5)
        else:
            raise RuntimeError("QMP connection failed")

        # Leer saludo inicial
        greeting = self._recv_json()

        # Habilitar capabilities
        self.execute("qmp_capabilities")

        self._running = True
        self._listener_thread = threading.Thread(
            target=self._listen,
            daemon=True
        )
        self._listener_thread.start()

    # ------------------------
    # SEND COMMAND
    # ------------------------

    def execute(self, command, arguments=None):
        payload = {
            "execute": command
        }

        if arguments:
            payload["arguments"] = arguments

        self._send_json(payload)
        return self._recv_json()

    # ------------------------
    # LOW LEVEL JSON
    # ------------------------

    def _send_json(self, data):
        message = json.dumps(data).encode("utf-8") + b"\r\n"
        self.socket.sendall(message)

    def _recv_json(self):
        buffer = b""
        while True:
            chunk = self.socket.recv(4096)
            if not chunk:
                break
            buffer += chunk
            if b"\r\n" in buffer:
                line, buffer = buffer.split(b"\r\n", 1)
                return json.loads(line.decode())

    # ------------------------
    # LISTENER (EVENTS)
    # ------------------------

    def _listen(self):
        while self._running:
            try:
                event = self._recv_json()
                if event and "event" in event:
                    if self.event_bus:
                        self.event_bus.emit("qmp_event", event)
            except Exception:
                break

    # ------------------------
    # CLEANUP
    # ------------------------

    def close(self):
        self._running = False
        if self.socket:
            self.socket.close()
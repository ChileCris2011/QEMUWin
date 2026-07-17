import socket
import json
import threading
import uuid
import time

class QMPClient:
    def __init__(self, host="127.0.0.1", port=4444):
        self.host = host
        self.port = port
        self.sock = None

        self._buffer = b""
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)

        self._responses = {}   # id -> response
        self._event_listeners = []
        self._running = False
        self._reader_thread = None

    # ---------------------------------
    # Connection
    # ---------------------------------

    def connect(self):
        self.sock = socket.create_connection((self.host, self.port))

        greeting = self._recv_message()
        if "QMP" not in greeting:
            raise RuntimeError("Invalid QMP greeting")

        self._running = True
        self._reader_thread = threading.Thread(
            target=self._reader_loop,
            daemon=True
        )
        self._reader_thread.start()

        self.execute("qmp_capabilities")

    def _wait_for_qmp(self, host="127.0.0.1", port=4444, timeout=10):
        start = time.time()
        while time.time() - start < timeout:
            try:
                sock = socket.create_connection((host, port), timeout=1)
                sock.close()
                return True
            except OSError:
                time.sleep(0.2)
        return False

    # ---------------------------------
    # Reader thread
    # ---------------------------------

    def _reader_loop(self):
        while self._running:
            try:
                message = self._recv_message()

                with self._condition:
                    if "event" in message:
                        listeners = list(self._event_listeners)

                        for callback in listeners:
                            try:
                                callback(message)
                            except Exception:
                                pass
                            
                        print(f"Got raw event {message}")
                    elif "id" in message:
                        self._responses[message["id"]] = message
                        print(f"Got raw response {message}")
                        self._condition.notify_all()

            except Exception:
                self._running = False
                break

    # ---------------------------------
    # Execute command
    # ---------------------------------

    def execute(self, command, arguments=None, timeout=10):
        cmd_id = str(uuid.uuid4())

        payload = {
            "execute": command,
            "id": cmd_id
        }

        if arguments:
            payload["arguments"] = arguments

        with self._condition:
            self._send(payload)

            if not self._condition.wait_for(
                lambda: cmd_id in self._responses,
                timeout=timeout
            ):
                raise TimeoutError("QMP command timeout")

            return self._responses.pop(cmd_id)

    # ---------------------------------
    # Messaging
    # ---------------------------------

    def _send(self, payload):
        data = (json.dumps(payload) + "\r\n").encode("utf-8")
        self.sock.sendall(data)

    def _recv_message(self):
        while b"\n" not in self._buffer:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise ConnectionError("QMP closed")
            self._buffer += chunk

        line, self._buffer = self._buffer.split(b"\n", 1)
        print(f"Raw received: {json.loads(line.decode("utf-8"))}")
        return json.loads(line.decode("utf-8"))

    # ---------------------------------
    # Events
    # ---------------------------------

    def add_event_listener(self, callback):
        with self._lock:
            self._event_listeners.append(callback)
    
    def remove_event_listener(self, callback):
        with self._lock:
            if callback in self._event_listeners:
                self._event_listeners.remove(callback)

    # ---------------------------------
    # High level
    # ---------------------------------

    def shutdown(self):
        return self.execute("system_powerdown")

    def quit(self):
        return self.execute("quit")
    
    def pause(self):
        return self.execute("stop")
    
    def resume(self):
        return self.execute("cont")

    def close(self):
        self._running = False
        if self.sock:
            self.sock.close()
            self.sock = None
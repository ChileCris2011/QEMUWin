# core/event_bus.py
import threading

class EventBus:
    def __init__(self):
        self._listeners = {}
        self._lock = threading.Lock()

    def subscribe(self, event_name, callback):
        with self._lock:
            self._listeners.setdefault(event_name, []).append(callback)

    def emit(self, event_name, *args, **kwargs):
        with self._lock:
            listeners = list(self._listeners.get(event_name, []))

        for callback in listeners:
            try:
                callback(*args, **kwargs)
            except Exception as e:
                print(f"Event error: {e}")
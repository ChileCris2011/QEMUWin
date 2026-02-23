# core/vm_state_controller.py
import threading
from vm_state import VMState

class VMStateController:

    def __init__(self, event_bus):
        self._state = VMState.PROCESS_STOPPED
        self._lock = threading.Lock()
        self.event_bus = event_bus

    def get_state(self):
        with self._lock:
            return self._state

    def set_state(self, new_state):
        with self._lock:
            if self._state == new_state:
                return
            self._state = new_state

        self.event_bus.emit("vm_state_changed", new_state)
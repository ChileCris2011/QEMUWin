# core/vm_state.py
from enum import Enum, auto
import threading

class VMState(Enum):
    PROCESS_STARTING = auto()
    PROCESS_RUNNING = auto()
    PROCESS_STOPPED = auto()
    PROCESS_CRASHED = auto()

    VM_RUNNING = auto()
    VM_PAUSED = auto()
    VM_SHUTDOWN = auto()
    VM_INTERNAL_ERROR = auto()

class VMStateMachine:

    VALID_TRANSITIONS = {
        VMState.PROCESS_STOPPED: [VMState.PROCESS_STARTING, VMState.PROCESS_CRASHED],
        VMState.PROCESS_STARTING: [VMState.PROCESS_RUNNING, VMState.PROCESS_CRASHED],
        VMState.PROCESS_RUNNING: [VMState.VM_RUNNING, VMState.PROCESS_CRASHED],
        VMState.VM_RUNNING: [VMState.VM_PAUSED, VMState.VM_SHUTDOWN, VMState.PROCESS_CRASHED],
        VMState.VM_PAUSED: [VMState.VM_RUNNING, VMState.VM_SHUTDOWN],
        VMState.VM_SHUTDOWN: [VMState.PROCESS_STOPPED],
        VMState.PROCESS_CRASHED: [VMState.PROCESS_STOPPED],
    }

    def __init__(self, event_bus):
        self._state = VMState.PROCESS_STOPPED
        self._lock = threading.Lock()
        self.event_bus = event_bus

    def get_state(self):
        with self._lock:
            return self._state

    def transition(self, new_state):
        with self._lock:
            if new_state not in self.VALID_TRANSITIONS[self._state]:
                raise RuntimeError(
                    f"Invalid transition {self._state} → {new_state}"
                )
            self._state = new_state

        self.event_bus.emit("vm_state_changed", new_state)
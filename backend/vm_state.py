from enum import Enum

class VMState(Enum):
    STOPPED = "stopped"
    KILLED = "killed"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
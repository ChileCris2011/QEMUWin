from enum import Enum

class VMState(Enum):
    STOPPING = "stopping"
    STOPPED = "stopped"
    KILLED = "killed"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
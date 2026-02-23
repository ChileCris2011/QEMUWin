# core/vm_instance.py
from drivers.qemu_command_builder import QEMUCommandBuilder
from core.qemu_process import QEMUProcess
from drivers.qmp_client import QMPClient
from core.vm_state import VMStateMachine, VMState

class VMInstance:

    def __init__(self, config, qemu_path, event_bus):
        self.config = config
        self.event_bus = event_bus
        self.builder = QEMUCommandBuilder(qemu_path)
        self.process = None
        self.qmp = None
        self.state_machine = VMStateMachine(event_bus)
        self.event_bus.subscribe("qmp_event", self._handle_qmp_event)
        self.event_bus.subscribe("vm_crashed", self._handle_crash)

    def start(self):
        self.state_machine.transition(VMState.PROCESS_STARTING)

        command = self.builder.build(self.config)
        self.process = QEMUProcess(command, self.event_bus)
        self.process.start()

        self.state_machine.transition(VMState.PROCESS_RUNNING)

        if self.config.qmp_port:
            self.qmp = QMPClient(
                port=self.config.qmp_port,
                event_bus=self.event_bus
            )
            self.qmp.connect()

            self._sync_state_from_qmp()

    def _sync_state_from_qmp(self):
        response = self.qmp.execute("query-status")
        status = response.get("return", {}).get("status")

        mapping = {
            "running": VMState.VM_RUNNING,
            "paused": VMState.VM_PAUSED,
            "shutdown": VMState.VM_SHUTDOWN,
            "internal-error": VMState.VM_INTERNAL_ERROR
        }

        if status in mapping:
            self.state_machine.transition(mapping[status])

    def _handle_qmp_event(self, event):
        event_name = event.get("event")

        if event_name == "SHUTDOWN":
            self.state_machine.transition(VMState.VM_SHUTDOWN)

        elif event_name == "STOP":
            self.state_machine.transition(VMState.VM_PAUSED)

        elif event_name == "RESUME":
            self.state_machine.transition(VMState.VM_RUNNING)

        elif event_name == "RESET":
            self.state_machine.transition(VMState.VM_RUNNING)

    def _handle_crash(self):
        self.state_machine.transition(VMState.PROCESS_CRASHED)

    def shutdown(self):
        if self.qmp:
            self.qmp.execute("system_powerdown")

    def reset(self):
        if self.qmp:
            self.qmp.execute("system_reset")

    def stop(self):
        if self.qmp:
            self.qmp.close()
        if self.process:
            self.process.stop(force=True)

        self.state_machine.transition(VMState.PROCESS_STOPPED)

    def is_running(self):
        return self.process and self.process.is_running()
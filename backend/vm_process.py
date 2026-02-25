import subprocess
import threading
from backend.vm_state import VMState
from backend.qmp_client import QMPClient


class VMProcess:
    def __init__(self, name, config, qmp_port):
        self.name = name
        self.config = config
        self.qmp_port = qmp_port
        self.process = None
        self.state = VMState.STOPPED
        self.qmp = None

        self.on_state_changed = None
        self.on_stopped = None

    def _set_state(self, state):
        self.state = state
        if self.on_state_changed:
            self.on_state_changed(self.name, state)

    def start(self):
        if self.state != VMState.STOPPED:
            return

        self._set_state(VMState.STARTING)

        cmd = self._build_command()
        self.process = subprocess.Popen(cmd)

        threading.Thread(target=self._monitor, daemon=True).start()

        try:
            self.qmp = QMPClient("127.0.0.1", self.qmp_port)
            self.qmp.connect()
            print("VM Running")
            self._set_state(VMState.RUNNING)
        except ConnectionRefusedError as e:
            print(f"Error Connecting to VM's QMP: {e}")
            self._set_state(VMState.ERROR)

    def _build_command(self):
        cmd = [f"C:\\msys64\\ucrt64\\bin\\qemu-system-x86_64.exe"]

        #print(cmd)

        cmd += [
            "-m", str(self.config.get("memory")),
            "-machine", "pc" if self.config.get("machine") == "pc-i440fx" else self.config.get("machine"),
            "-qmp", f"tcp:127.0.0.1:{self.qmp_port},server,nowait"
        ]

        #print(cmd)

        cpu_type = self.config.get("cpu")

        cmd += [
            "-cpu", cpu_type.get("model"),
            "-smp", str(cpu_type.get("cores"))
        ]

        #print(cmd)

        if self.config.get("storage"):
            for disk in self.config.get("storage"):
                cmd += ["-drive", f"media=disk,file={disk.get("path")},format={disk.get("format")},if={disk.get("bus")}"]

        #print(cmd)

        if self.config.get("media"):
            for medias in self.config.get("media"):
                cmd += ["-drive"]
                if medias.get("type") == "CD-ROM":
                    if medias.get("path") != "Empty":
                        cmd += [f"media=cdrom,file={medias.get("path")},if=ide"]
                    else:
                        cmd += ["media=cdrom,if=ide"]
                elif medias.get("type") == "Floppy":
                    if medias.get("path") != "Empty":
                        cmd += [f"file=\"{medias.get("path")}\",if=floppy"]
                    else:
                        cmd += ["if=floppy"]

        #print(cmd)

        if self.config.get("enable_whpx"):
            cmd += ["-accel", "whpx"]

        #print(cmd)

        if self.config.get("vnc_port"):
            cmd += ["-vnc", f":{self.config.vnc_port}"]
        
        #print(cmd)

        if self.config.get("custom_flags"):
            cmd += self.config.get("custom_flags")

        #print(cmd)

        print(f"Command generated: {" ".join(cmd)}")
        return cmd

    def _monitor(self):
        self.process.wait()
        self._set_state(VMState.STOPPED)

        if self.on_stopped:
            self.on_stopped(self.name)

    def stop(self):
        if self.qmp:
            try:
                self.qmp.shutdown()
            except:
                pass
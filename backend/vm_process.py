import subprocess
import threading

from backend.vm_state import VMState
from backend.qmp_client import QMPClient
from backend.vm_meta import VMMetadata

import logging

class VMProcess:
    def __init__(self, name, config, qmp_port, vnc_port=None):
        self.name = name
        self.config = config
        self.qmp_port = qmp_port
        self.vnc_port = vnc_port
        self.process = None
        self.state = VMState.STOPPED
        self.qmp = None

        self.metadata = VMMetadata(f"meta")

        self.killed = False

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
        self.process = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)

        threading.Thread(target=self._monitor, daemon=True).start()

        try:
            self.qmp = QMPClient("127.0.0.1", self.qmp_port)

            if not self.qmp._wait_for_qmp(port=self.qmp_port):
                logging.error(f"Timeout for VM's QMP")
                self._set_state(VMState.ERROR)
                return
            self.qmp.connect()

            logging.info("VM Running")
            self._set_state(VMState.RUNNING)
            self.qmp.add_event_listener(self._handle_qmp_event)

            self.metadata.save({
                "name": self.name,
                "qmp_port": self.qmp_port,
                "vnc_port": self.vnc_port,
                "pid": self.process.pid,
                "started_by_manager": True,
                "last_state": "RUNNING"
            }, self.name)

        except ConnectionRefusedError as e:
            logging.error(f"Error Connecting to VM's QMP")
            self._set_state(VMState.ERROR)

            from gui.error_dialog import ErrorDialog
            error = ErrorDialog("Error Connecting to VM's QMP", e)
            error.exec()

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
                cmd += ["-drive", f"media=disk,file={disk.get("path")},format={self._detect_format(disk.get("path"))},if={disk.get("bus")}"]

        #print(cmd)

        empty_text = ["Empty", "", " ", "empty"]

        if self.config.get("media"):
            for medias in self.config.get("media"):
                cmd += ["-drive"]
                if medias.get("type") == "CD-ROM":
                    if medias.get("path") not in empty_text:
                        cmd += [f"media=cdrom,file={medias.get("path")},if=ide,id=cdrom{medias.get("id")}"]
                    else:
                        cmd += [f"media=cdrom,if=ide,id=cdrom{medias.get("id")}"]
                elif medias.get("type") == "Floppy":
                    if medias.get("path") not in empty_text:
                        cmd += [f"file=\"{medias.get("path")}\",if=floppy,id=floppy{medias.get("id")}"]
                    else:
                        cmd += [f"if=floppy,id=floppy{medias.get("id")}"]

        #print(cmd)

        if self.config.get("enable_whpx"):
            cmd += ["-accel", "whpx"]

        #print(cmd)

        if self.config.get("vnc"):
            cmd += ["-vnc", f":{self.config["vnc"] - 5900}"]
        
        #print(cmd)

        if self.config.get("qargs"):
            cmd += self.config.get("qargs")

        #print(cmd)

        logging.debug(f"Command generated: {" ".join(cmd)}")
        return cmd

    def _detect_format(self, path):

        try:
            result = subprocess.run(
                ["qemu-img", "info", path],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            for line in result.stdout.splitlines():
                if "file format" in line:
                    return line.split(":")[1].strip()

        except Exception:
            pass

        return "raw"

    def _handle_qmp_event(self, event):
        ev = event.get("event")
        print(f"Got event {ev}")

        if ev == "SHUTDOWN":
            self._set_state(VMState.STOPPED)

        elif ev == "STOP":
            self._set_state(VMState.PAUSED)

        elif ev == "RESUME":
            self._set_state(VMState.RUNNING)
    
    def restore_vm(self):
        data = self.metadata.load(self.name)
        if not data:
            self._set_state(VMState.STOPPED)
            return None

        try:
            logging.debug(f"Connecting to QMP:{data["qmp_port"]}")
            qmp = QMPClient("127.0.0.1", data["qmp_port"])

            qmp.connect()

            status = qmp.execute("query-status")
            run_state = status["return"]["status"]
            logging.debug("...")

            self.qmp = qmp
            self.qmp_port = data["qmp_port"]

            if run_state == "running":
                self._set_state(VMState.RUNNING)
                act_state = "running"
            elif run_state == "paused":
                self._set_state(VMState.PAUSED)
                act_state = "paused"
            else:
                self._set_state(VMState.STOPPED)
                act_state = "stopped"

            self.qmp.add_event_listener(self._handle_qmp_event)

            return {
                "name": data["name"],
                "state": act_state
            }

        except Exception:
            pass

        self.metadata.delete(self.name)
        self._set_state(VMState.STOPPED)

        return None

    def _monitor(self):
        code = self.process.wait()

        if self.state not in (VMState.STOPPING, VMState.STOPPED):
            if code == 0:
                if self.killed:
                    self._set_state(VMState.KILLED)
                else:
                    self._set_state(VMState.STOPPED)
            else:
                self._set_state(VMState.ERROR)

        self.metadata.delete(self.name)

        if self.on_stopped:
            self.on_stopped(self.name)

    def stop(self):
        if self.qmp:
            try:
                self.qmp.shutdown()
            except:
                raise RuntimeError("Failed to send ACPI Shutdown signal to VM")
    def quit(self):
        if self.qmp:
            try:
                self.qmp.quit()
                self.killed = True
            except:
                raise RuntimeError("Failed to end VM process")
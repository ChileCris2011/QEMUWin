# core/qemu_process.py
import subprocess
import threading

class QEMUProcess:

    def __init__(self, command, event_bus):
        self.command = command
        self.event_bus = event_bus
        self.process = None
        self._stdout_thread = None
        self._watcher_thread = None
        self._running = False

    # ------------------------
    # START
    # ------------------------

    def start(self):
        if self._running:
            return

        self.process = subprocess.Popen(
            self.command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            text=True
        )

        self._running = True

        self._stdout_thread = threading.Thread(
            target=self._read_stdout,
            daemon=False
        )
        self._stdout_thread.start()

        self._watcher_thread = threading.Thread(
            target=self._watch_process,
            daemon=False
        )
        self._watcher_thread.start()

        self.event_bus.emit("vm_started")

    # ------------------------
    # STDOUT READER
    # ------------------------

    def _read_stdout(self):
        try:
            for line in self.process.stdout:
                if not self._running:
                    break
                self.event_bus.emit("vm_output", line.rstrip())
        except Exception as e:
            self.event_bus.emit("vm_error", str(e))

    # ------------------------
    # WATCHER
    # ------------------------

    def _watch_process(self):
        self.process.wait()
        self._running = False
        self.event_bus.emit("vm_stopped")
        if self.process.returncode != 0:
            self.event_bus.emit("vm_crashed")

    # ------------------------
    # STOP
    # ------------------------

    def stop(self, force=False):
        if not self.process or not self._running:
            return

        self._running = False

        if force:
            self.process.kill()
        else:
            self.process.terminate()

        self.process.wait()

    # ------------------------
    # STATUS
    # ------------------------

    def is_running(self):
        return self._running and self.process.poll() is None
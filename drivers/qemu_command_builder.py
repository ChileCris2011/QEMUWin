# drivers/qemu_command_builder.py
from pathlib import Path
from config.vm_config import VMConfig

class QEMUCommandBuilder:

    def __init__(self, qemu_path: str):
        self.qemu_path = qemu_path

    def build(self, config: VMConfig) -> list:
        cmd = [self.qemu_path]

        cmd += [
            "-m", str(config.memory_mb),
            "-smp", str(config.cpu_cores),
            "-machine", config.machine_type,
            "-drive", f"file={config.disk_path},format=qcow2"
        ]

        if config.iso_path:
            cmd += ["-cdrom", config.iso_path]

        if config.enable_whpx:
            cmd += ["-accel", "whpx"]

        if config.qmp_port:
            cmd += ["-qmp", f"tcp:127.0.0.1:{config.qmp_port},server,nowait"]

        if config.vnc_port:
            cmd += ["-vnc", f":{config.vnc_port}"]

        # Flags personalizados (clave en tu diseño)
        cmd += config.custom_flags

        return cmd
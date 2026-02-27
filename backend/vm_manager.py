from backend.config_manager import ConfigManager
from backend.vm_process import VMProcess
from backend.vm_state import VMState
from backend.port_manager import QMPPortManager

import subprocess, os, logging


class VMManager:
    def __init__(self):
        self.config = ConfigManager()
        self.processes = {}
        self.port_manager = QMPPortManager()

        self.on_vm_state_changed = None

    def list_vms(self):
        return self.config.list_vms()

    def vm_exists(self, name):
        return name in self.config.list_vms()

    def create_vm(self, name, data):
        if self.vm_exists(name):
            raise ValueError("VM already exists")
        
        data = self._prepare_storage(data)

        self.config.save_vm(name, data)

    def edit_vm(self, name, data):
        if not self.vm_exists(name):
            raise ValueError("VM does not exist")

        if name in self.processes:
            raise RuntimeError("Cannot edit running VM")
        
        if (data.get("name") != name):
            self.config.delete_vm(name)
            name = data.get("name")


        self.config.save_vm(name, data)

    def delete_vm(self, name):
        if name in self.processes:
            raise RuntimeError("Cannot delete running VM")

        self.config.delete_vm(name)

    def start_vm(self, name):
        if name in self.processes:
            return

        config = self.config.load_vm(name)
        if config.get("qmp_port"):
            qmp_port = config.get("qmp_port")
        else:
            qmp_port = self.port_manager.get_free_port()

        vm = VMProcess(name, config, qmp_port)
        vm.on_state_changed = self._vm_state_changed
        vm.on_stopped = self._vm_stopped

        self.processes[name] = vm
        vm.start()

    def stop_vm(self, name):
        if name in self.processes:
            self.processes[name].stop()

    def kill_vm(self, name):
        if name in self.processes:
            self.processes[name].quit()

    def _vm_state_changed(self, name, state):
        if self.on_vm_state_changed:
            self.on_vm_state_changed(name, state)

    def _vm_stopped(self, name):
        if name in self.processes:
            port = self.processes[name].qmp_port
            self.port_manager.release_port(port)
            del self.processes[name]

    def get_state(self, name):
        if name in self.processes:
            return self.processes[name].state
        return VMState.STOPPED
    
    def _prepare_storage(self, config):

        final_storage = []

        for disk in config.get("storage", []):

            mode = disk.get("mode")

            if mode == "create":
                self._create_disk_file(disk)
                disk["path"] = f"{disk["path"]}\\{disk["name"]}.{disk["fmat"]}"
                disk.pop("size", None)
                disk.pop("fmat", None)
                disk.pop("name")

            # Delete creation tag
            disk.pop("mode", None)

            final_storage.append(disk)

        config["storage"] = final_storage
        return config


    def _create_disk_file(self, disk):

        path = f"{disk["path"]}\\{disk["name"]}.{disk["fmat"]}"
        size = disk["size"]
        fmt = disk["fmat"]

        # Make folder if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # qemu-img create
        cmd = [
            "qemu-img",
            "create",
            "-f", fmt,
            path,
            f"{size}G"
        ]

        command = subprocess.run(cmd, capture_output=True)

        if command.returncode != 0:
            logging.error(command.stderr)
            logging.error(command.stdout.decode())
        else:
            logging.debug(command.stdout.decode())

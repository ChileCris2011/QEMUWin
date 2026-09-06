from backend.config_manager import ConfigManager
from backend.vm_process import VMProcess
from backend.vm_state import VMState
from backend.port_manager import PortManager

import subprocess, os, logging


class VMManager:
    def __init__(self, app):
        self.config = ConfigManager()
        self.processes = {}
        self.port_manager = PortManager()

        self.app = app
        self.vnc_window = None

        self.on_vm_state_changed = None
        self.vm_stopped = None

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

    def restore_vms(self):
        vms = self.list_vms()
        for name in vms:
            logging.debug(f"Trying to restore VM {name}")
            config = self.config.load_vm(name)
            vm = VMProcess(name, config, None, None)
            logging.debug("...")
            result = vm.restore_vm()
            if result:
                vm.on_state_changed = self._vm_state_changed
                vm.on_stopped = self._vm_stopped
                self.processes[name] = vm
                logging.info(f"Restored VM {name}")

                vm.on_state_changed(result.get("name"), VMState(result.get("state")))

    def start_vm(self, name):
        if name in self.processes:
            return

        config = self.config.load_vm(name)
        if config.get("qmp_port"):
            qmp_port = config.get("qmp_port")
        else:
            qmp_port = self.port_manager.get_free_port(4444)

        if config["video"]["connection"] == "VNC":
            vnc_port = config["video"].get("port", 0)
            if vnc_port < 5900:
                vnc_port = self.port_manager.get_free_port(5900)
        else:
            vnc_port = None

        vm = VMProcess(name, config, qmp_port, vnc_port)
        vm.on_state_changed = self._vm_state_changed
        vm.on_stopped = self._vm_stopped

        self.processes[name] = vm

        print(self.processes)

        try:
            vm.start()
        except Exception:
            self._remove_process(name)
            raise

        return {
            "config": config,
            "process": vm
        }
    
    def pause_vm(self, name):
        if name in self.processes:
            self.processes[name].pause()
    
    def resume_vm(self, name):
        if name in self.processes:
            self.processes[name].resume()

    def change_media(self, name, media):
        if name in self.processes:
            self.processes[name].change_media(media)

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
        self._remove_process(name)
        
        if self.vm_stopped:
            self.vm_stopped(name)

    def _remove_process(self, name):
        if name in self.processes:
            process = self.processes[name]
            self.port_manager.release_port(process.qmp_port)
            self.port_manager.release_port(process.vnc_port)
            del self.processes[name]
            print(self.processes)

    def get_state(self, name):
        if name in self.processes:
            return self.processes[name].state
        return VMState.STOPPED
    
    def _prepare_storage(self, config):

        final_storage = []

        dsk = 0
        for disk in config.get("storage", []):

            mode = disk.get("mode")

            if mode == "create":
                self._create_disk_file(disk)
                disk["path"] = os.path.join(disk["path"], f"{disk["name"]}.{disk["fmat"]}")
                disk.pop("size", None)
                disk.pop("fmat", None)
                disk.pop("name")

            disk["id"] = dsk
            dsk += 1
            # Delete creation tag
            disk.pop("mode", None)

            final_storage.append(disk)
        
        final_media = []
        cd = 0
        floppy = 0
        for media in config.get("media", []):
            if media["type"] == "CD-ROM":
                media["id"] = cd
                cd += 1
            elif media["type"] == "Floppy":
                media["id"] = floppy
                floppy += 1
                
            final_media.append(media)

        config["storage"] = final_storage
        config["media"] = final_media
        return config


    def _create_disk_file(self, disk):

        path = os.path.join(disk["path"], f"{disk["name"]}.{disk["fmat"]}")
        size = disk["size"]
        fmt = disk["fmat"]

        # Make folder if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)

        from PyQt6.QtCore import QSettings

        setts = QSettings("QEMUWin", "QEMUWin")

        # qemu-img create

        cmd = []

        if setts.value("qemu/path", False):
            cmd += [
                os.path.join(setts.value("qemu/path"), "qemu-img.exe")
            ]
        else:
            cmd = [
                "qemu-img.exe"
            ]

        cmd += [
            "create",
            "-f", fmt,
            path,
            f"{size}G"
        ]

        try:
            command = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        except FileNotFoundError as e:
            logging.error("\'qemu-img\' is not accessible or doesn't exists")
            raise RuntimeError("\'qemu-img\' is not accessible or doesn't exist") from e

        if command.returncode != 0:
            logging.error(command.stderr)
            logging.error(command.stdout)
            raise RuntimeError(command.stderr or "Failed to create disk image")
        else:
            logging.debug(command.stdout)

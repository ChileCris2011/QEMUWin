# core/vm_manager.py
from config.vm_storage import VMStorage
from core.vm_instance import VMInstance

class VMManager:

    def __init__(self, qemu_path):
        from core.event_bus import EventBus
        from core.port_manager import PortManager

        self.event_bus = EventBus()
        self.port_manager = PortManager()
        self.qemu_path = qemu_path
        self.storage = VMStorage()
        self.vms = {}

        self._load_existing_vms()

    def _load_existing_vms(self):
        configs = self.storage.load_all()

        for config in configs:
            vm = VMInstance(config, self.qemu_path, self.event_bus)
            self.vms[config.name] = vm

    def _release_ports(self, name):
        vm = self.vms.get(name)
        if not vm:
            print("Tried to release a port of a non exixtent vm")
            return

        config = vm.config

        if config.qmp_port:
            self.port_manager.release(config.qmp_port)

        if config.vnc_port:
            self.port_manager.release(config.vnc_port)

    def create_vm(self, config):
        if config.qmp_port is None:
            config.qmp_port = self.port_manager.allocate_qmp()

        if config.vnc_port is None:
            config.vnc_port = self.port_manager.allocate_vnc()

        self.storage.save(config)

        vm = VMInstance(config, self.qemu_path, self.event_bus)
        self.event_bus.subscribe("vm_stopped",
            lambda name=config.name: self._release_ports(name)
        )
        self.vms[config.name] = vm

        return vm
    
    def delete_vm(self, name):
        if name in self.vms:
            self.vms[name].stop()
            del self.vms[name]

        self.storage.delete(name)

    def get_vm(self, name):
        return self.vms.get(name)

    def list_vms(self):
        return list(self.vms.keys())
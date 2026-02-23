from core.vm_manager import VMManager

manager = VMManager(f"C:\\msys64\\ucrt64\\bin\\qemu-system-x86_64.exe")

vms = manager.list_vms()

print("VMs disponibles: ", vms)

sourcevm = input(f"Select the VM to start (0-{len(vms)-1})")

vm = manager.get_vm(vms[int(sourcevm)])

manager.event_bus.subscribe("vm_output", print)
manager.event_bus.subscribe("vm_started", lambda: print("VM started"))
manager.event_bus.subscribe("vm_stopped", lambda: print("VM stopped"))

try:
    vm.start()
except KeyboardInterrupt:
    vm.shutdown()
import os
import json

class ConfigManager:
    def __init__(self, vm_dir="vms"):
        self.vm_dir = vm_dir
        os.makedirs(self.vm_dir, exist_ok=True)

    def list_vms(self):
        return [
            f.replace(".json", "")
            for f in os.listdir(self.vm_dir)
            if f.endswith(".json")
        ]

    def load_vm(self, name):
        path = os.path.join(self.vm_dir, f"{name}.json")
        with open(path, "r") as f:
            return json.load(f)

    def save_vm(self, name, data):
        path = os.path.join(self.vm_dir, f"{name}.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=4)

    def delete_vm(self, name):
        path = os.path.join(self.vm_dir, f"{name}.json")
        if os.path.exists(path):
            os.remove(path)
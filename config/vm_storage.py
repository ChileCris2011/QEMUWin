# config/vm_storage.py

import os
from pathlib import Path
from config.vm_config import VMConfig


class VMStorage:

    def __init__(self, base_path="data/vms"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    # ------------------------
    # PATH
    # ------------------------

    def _vm_path(self, name: str):
        return self.base_path / f"{name}.json"

    # ------------------------
    # SAVE
    # ------------------------

    def save(self, config: VMConfig):
        path = self._vm_path(config.name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(config.to_json())

    # ------------------------
    # LOAD ONE
    # ------------------------

    def load(self, name: str) -> VMConfig:
        path = self._vm_path(name)
        if not path.exists():
            raise FileNotFoundError(f"VM config not found: {name}")

        with open(path, "r", encoding="utf-8") as f:
            return VMConfig.from_json(f.read())

    # ------------------------
    # LOAD ALL
    # ------------------------

    def load_all(self):
        configs = []

        for file in self.base_path.glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                configs.append(VMConfig.from_json(f.read()))

        return configs

    # ------------------------
    # DELETE
    # ------------------------

    def delete(self, name: str):
        path = self._vm_path(name)
        if path.exists():
            path.unlink()

    # ------------------------
    # LIST
    # ------------------------

    def list(self):
        return [file.stem for file in self.base_path.glob("*.json")]
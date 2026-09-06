import os
import json
import shutil

class ConfigManager:
    INVALID_FILENAME_CHARS = set('<>:"/\\|?*()')
    RESERVED_FILENAMES = {
        "CON", "PRN", "AUX", "NUL",
        "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
    }

    def __init__(self, vm_dir="vms"):
        self.vm_dir = vm_dir
        os.makedirs(self.vm_dir, exist_ok=True)
        os.makedirs(os.path.join(self.vm_dir, "backups"), exist_ok=True)

    @classmethod
    def sanitize_filename(cls, name):
        safe_name = "".join(
            "_" if char in cls.INVALID_FILENAME_CHARS or ord(char) < 32 else char
            for char in str(name)
        )
        safe_name = safe_name.strip(" .")

        if not safe_name:
            safe_name = "vm"

        stem = safe_name.split(".")[0].upper()
        if stem in cls.RESERVED_FILENAMES:
            safe_name = f"_{safe_name}"

        return safe_name

    def list_vms(self):
        names = []
        for path in self._iter_vm_paths():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                names.append(config.get("name") or os.path.splitext(os.path.basename(path))[0])
            except (OSError, json.JSONDecodeError):
                names.append(os.path.splitext(os.path.basename(path))[0])
        return names

    def load_vm(self, name):
        path = self._resolve_vm_path(name)
        if not path:
            raise FileNotFoundError(name)
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_vm(self, name, data):
        vm_name = data.get("name") or name
        path = self._find_vm_path_by_name(vm_name) or self._available_vm_path(vm_name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def delete_vm(self, name):
        path = self._resolve_vm_path(name)
        if path and os.path.exists(path):
            os.remove(path)
    
    def backup_vm(self, name):
        path = self._resolve_vm_path(name)
        if not path:
            raise FileNotFoundError(name)
        new_path = os.path.join(self.vm_dir, "backups", os.path.basename(path))
        shutil.copy(
            path,
            new_path
        )

    def normalize_vm_filename(self, name):
        current_path = self._resolve_vm_path(name)
        if not current_path or not os.path.exists(current_path):
            raise FileNotFoundError(name)

        target_path = self._path_for_vm_name(name)
        if os.path.normcase(current_path) == os.path.normcase(target_path):
            return current_path

        if os.path.exists(target_path):
            target_path = self._available_vm_path(name)

        os.replace(current_path, target_path)
        return target_path

    def _iter_vm_paths(self):
        for filename in os.listdir(self.vm_dir):
            path = os.path.join(self.vm_dir, filename)
            if os.path.isfile(path) and filename.endswith(".json"):
                yield path

    def _resolve_vm_path(self, name):
        return self._find_vm_path_by_name(name) or self._legacy_vm_path(name)

    def _find_vm_path_by_name(self, name):
        for path in self._iter_vm_paths():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except (OSError, json.JSONDecodeError):
                continue

            if config.get("name") == name:
                return path

        return None

    def _available_vm_path(self, name):
        safe_name = self.sanitize_filename(name)
        path = self._path_for_safe_name(safe_name)
        if not os.path.exists(path):
            return path

        index = 2
        while True:
            path = self._path_for_safe_name(f"{safe_name}_{index}")
            if not os.path.exists(path):
                return path
            index += 1

    def _path_for_vm_name(self, name):
        return self._path_for_safe_name(self.sanitize_filename(name))

    def _path_for_safe_name(self, safe_name):
        return os.path.join(self.vm_dir, f"{safe_name}.json")

    def _legacy_vm_path(self, name):
        path = self._path_for_vm_name(name)
        if not os.path.exists(path):
            return path

        try:
            with open(path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except (OSError, json.JSONDecodeError):
            return path

        if not config.get("name") or config.get("name") == name:
            return path

        return None

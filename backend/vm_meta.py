import json
import os
from backend.config_manager import ConfigManager

class VMMetadata:
    def __init__(self, path):
        self.path = path
        os.makedirs(self.path, exist_ok=True)

    def save(self, data: dict, name):
        metadata_name = data.get("name") or name
        path = self._find_metadata_path_by_name(metadata_name) or self._available_metadata_path(metadata_name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def load(self, name):
        path = self._resolve_metadata_path(name)
        if not path or not os.path.exists(path):
            return None
        
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def delete(self, name):
        path = self._resolve_metadata_path(name)
        if path and os.path.exists(path):
            os.remove(path)

    def _iter_metadata_paths(self):
        for filename in os.listdir(self.path):
            path = os.path.join(self.path, filename)
            if os.path.isfile(path) and filename.endswith(".json"):
                yield path

    def _resolve_metadata_path(self, name):
        return self._find_metadata_path_by_name(name) or self._legacy_metadata_path(name)

    def _find_metadata_path_by_name(self, name):
        for path in self._iter_metadata_paths():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except (OSError, json.JSONDecodeError):
                continue

            if data.get("name") == name:
                return path

        return None

    def _available_metadata_path(self, name):
        safe_name = ConfigManager.sanitize_filename(name)
        path = self._path_for_safe_name(safe_name)
        if not os.path.exists(path):
            return path

        index = 2
        while True:
            path = self._path_for_safe_name(f"{safe_name}_{index}")
            if not os.path.exists(path):
                return path
            index += 1

    def _path_for_name(self, name):
        return self._path_for_safe_name(ConfigManager.sanitize_filename(name))

    def _path_for_safe_name(self, safe_name):
        return os.path.join(self.path, f"{safe_name}.json")

    def _legacy_metadata_path(self, name):
        path = self._path_for_name(name)
        if not os.path.exists(path):
            return path

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return path

        if not data.get("name") or data.get("name") == name:
            return path

        return None

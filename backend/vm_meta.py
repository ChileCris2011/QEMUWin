import json
import os

class VMMetadata:
    def __init__(self, path):
        self.path = path

    def save(self, data: dict, name):
        with open(f"{self.path}/{name}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def load(self, name):
        if not os.path.exists(f"{self.path}/{name}.json"):
            return None
        
        with open(f"{self.path}/{name}.json", "r", encoding="utf-8") as f:
            return json.load(f)

    def delete(self, name):
        if os.path.exists(f"{self.path}/{name}.json"):
            os.remove(f"{self.path}/{name}.json")
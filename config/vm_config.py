# config/vm_config.py

from dataclasses import dataclass, asdict, field
from typing import List, Optional
import json


@dataclass
class VMConfig:
    name: str
    memory_mb: int
    cpu_cores: int
    disk_path: str

    iso_path: Optional[str] = None
    machine_type: str = "pc"
    enable_whpx: bool = False
    qmp_port: Optional[int] = None
    vnc_port: Optional[int] = None
    custom_flags: List[str] = field(default_factory=list)

    # ------------------------
    # SERIALIZATION
    # ------------------------

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str):
        return cls.from_dict(json.loads(json_str))
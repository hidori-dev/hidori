from typing import Dict, Type
from hidori_core.schema.base import Schema

MODULES_REGISTRY: Dict[str, "Module"] = {}

class Module:
    def __init_subclass__(cls, /, name: str, schema_cls: Type[Schema]) -> None:
        super().__init_subclass__()

        if name in MODULES_REGISTRY:
            raise RuntimeError(f"{name} module is already registered.")
        MODULES_REGISTRY[name] = cls(schema_cls)

    def __init__(self, schema_cls: Type[Schema]) -> None:
        self.schema = schema_cls()
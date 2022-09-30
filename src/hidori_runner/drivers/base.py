from typing import Any

from hidori_core.schema.base import Schema

DRIVERS_REGISTRY: dict[str, type["Driver"]] = {}


class Driver:
    schema: Schema

    def __init_subclass__(cls, *, name: str, schema_cls: type[Schema]) -> None:
        super().__init_subclass__()

        if name in DRIVERS_REGISTRY:
            raise RuntimeError(f"{name} driver is already registered.")
        cls.schema = schema_cls()
        DRIVERS_REGISTRY[name] = cls

    def __init__(self, config: Any) -> None:
        self.schema.validate(config)

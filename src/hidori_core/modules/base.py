from typing import Any, Dict, Type

from hidori_core.schema.base import Schema
from hidori_core.schema.errors import SchemaError
from hidori_core.utils.messenger import Messenger

MODULES_REGISTRY: Dict[str, "Module"] = {}


class Module:
    def __init_subclass__(cls, *, name: str, schema_cls: Type[Schema]) -> None:
        super().__init_subclass__()

        if name in MODULES_REGISTRY:
            raise RuntimeError(f"{name} module is already registered.")
        MODULES_REGISTRY[name] = cls(schema_cls)

    def __init__(self, schema_cls: Type[Schema]) -> None:
        self.schema = schema_cls()

    def validate_and_execute(
        self, task_data: Dict[str, Any], messenger: Messenger
    ) -> Dict[str, str]:
        try:
            validated_data = self.schema.validate(task_data)
        except SchemaError as e:
            module = task_data["module"]
            for field, error in e.errors.items():
                messenger.queue_error(f"module::{module}, field::{field}: {error}")
            return {"state": "error"}

        return self.execute(validated_data, messenger)

    def execute(
        self, validated_data: Dict[str, Any], messenger: Messenger
    ) -> Dict[str, str]:
        raise NotImplementedError()

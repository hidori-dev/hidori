import inspect
from typing import Any, Dict, Optional, Tuple, Type

from hidori_core.compat.typing import Literal
from hidori_core.schema.base import (
    Field,
    Schema,
    ValidationError,
    field_from_annotation,
)


class Text(Field):
    @classmethod
    def from_annotation(
        cls, annotation: Any, required: bool = True
    ) -> Optional["Text"]:
        return cls(required) if annotation == str else None

    def __init__(self, required: bool) -> None:
        self.required = required

    def validate(self, value: Optional[Any]) -> str:
        super().validate(value)
        if not isinstance(value, str):
            raise ValidationError(f"value `{value}` not allowed; is not str")

        return value


class OneOf(Field):
    @classmethod
    def from_annotation(
        cls, annotation: Any, required: bool = True
    ) -> Optional["OneOf"]:
        if getattr(annotation, "__origin__", None) == Literal:
            return cls(annotation.__args__, required)
        else:
            return None

    def __init__(self, values: Tuple[Any], required: bool) -> None:
        self.allowed_values = values
        self.required = required

    def validate(self, value: Optional[Any]) -> Optional[Any]:
        super().validate(value)

        if value in self.allowed_values:
            return value
        else:
            raise ValidationError(
                f"value `{value}` not allowed; allowed values are {self.allowed_values}"
            )


class SubSchema(Field):
    @classmethod
    def from_annotation(
        cls, annotation: Any, required: bool = True
    ) -> Optional["SubSchema"]:
        if inspect.isclass(annotation) and issubclass(annotation, Schema):
            return cls(annotation, required)
        else:
            return None

    def __init__(self, schema_cls: Type[Schema], required: bool) -> None:
        self.schema = schema_cls()
        self.required = required

    def validate(self, value: Optional[Any]) -> Optional[Any]:
        super().validate(value)
        if not isinstance(value, dict):
            raise ValidationError(f"value `{value}` not allowed; is not dict")

        self.schema.validate(value)
        return value


class Dictionary(Field):
    @classmethod
    def from_annotation(
        cls, annotation: Any, required: bool = True
    ) -> Optional["Dictionary"]:
        if getattr(annotation, "__origin__", None) == dict:
            return cls(annotation.__args__, required)
        else:
            return None

    def __init__(self, values: Tuple[Any, Any], required: bool) -> None:
        key_type, val_type = values
        self.key_field = field_from_annotation(key_type)
        self.val_field = field_from_annotation(val_type)
        self.required = required

    def validate(self, value: Optional[Any]) -> Dict[Any, Any]:
        super().validate(value)
        if not isinstance(value, dict):
            raise ValidationError(f"value `{value}` not allowed; is not dict")

        return self._validate_items(value)

    def _validate_items(self, value: Dict[Any, Any]) -> Dict[Any, Any]:
        for key, val in value.items():
            self.key_field.validate(key)
            self.val_field.validate(val)

        return value

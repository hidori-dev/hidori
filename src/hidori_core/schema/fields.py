import inspect
from typing import Any, Dict, Literal, Optional, Tuple, Type

from hidori_core.schema import errors as schema_errors
from hidori_core.schema.base import Field, Schema, field_from_annotation


class Anything(Field):
    @classmethod
    def from_annotation(
        cls, annotation: Any, required: bool = True
    ) -> Optional["Anything"]:
        return cls(required) if annotation == Any else None

    def __init__(self, required: bool) -> None:
        self.required = required

    def validate(self, value: Any) -> Any:
        super().validate(value)
        return value


class Text(Field):
    @classmethod
    def from_annotation(
        cls, annotation: Any, required: bool = True
    ) -> Optional["Text"]:
        return cls(required) if annotation is str else None

    def __init__(self, required: bool) -> None:
        self.required = required

    def validate(self, value: Any) -> str:
        super().validate(value)
        if not isinstance(value, str):
            raise schema_errors.ValidationError(
                f"expected str, got {type(value).__name__}"
            )
        return value


class OneOf(Field):
    @classmethod
    def from_annotation(
        cls, annotation: Any, required: bool = True
    ) -> Optional["OneOf"]:
        if getattr(annotation, "__origin__", None) is Literal:
            return cls(annotation.__args__, required)
        else:
            return None

    def __init__(self, values: Tuple[Any], required: bool) -> None:
        self.allowed_values = values
        self.required = required

    def validate(self, value: Any) -> Any:
        super().validate(value)
        if value not in self.allowed_values:
            raise schema_errors.ValidationError(
                f"not one of allowed values: {self.allowed_values}"
            )
        return value


class SubSchema(Field):
    @classmethod
    def from_annotation(
        cls, annotation: Any, required: bool = True
    ) -> Optional["SubSchema"]:
        if (
            inspect.isclass(annotation)
            and issubclass(annotation, Schema)
            and annotation is not Schema
        ):
            return cls(annotation, required)
        else:
            return None

    def __init__(self, schema_cls: Type[Schema], required: bool) -> None:
        self.schema = schema_cls()
        self.required = required

    def validate(self, value: Any) -> Dict[str, Any]:
        super().validate(value)
        if not isinstance(value, dict):
            raise schema_errors.ValidationError(
                f"expected dict, got {type(value).__name__}"
            )

        return self.schema.validate(value)


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

    def validate(self, value: Any) -> Dict[str, Any]:
        super().validate(value)
        if not isinstance(value, dict):
            raise schema_errors.ValidationError(
                f"expected dict, got {type(value).__name__}"
            )

        self._validate_items(value)
        return value

    def _validate_items(self, value: Dict[Any, Any]) -> Dict[Any, Any]:
        for key, val in value.items():
            self.key_field.validate(key)
            self.val_field.validate(val)

        return value

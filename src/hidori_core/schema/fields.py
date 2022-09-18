from typing import Any, Dict, Optional, Tuple

from hidori_core.compat.typing import Literal
from hidori_core.schema.base import Field, ValidationError, field_from_annotation


class Text(Field):
    @classmethod
    def from_annotation(
        cls, annotation: Any, required: bool = True
    ) -> Optional["Text"]:
        return cls(required) if annotation == str else None

    def __init__(self, required: bool) -> None:
        self.required = required


class OneOf(Field):
    @classmethod
    def from_annotation(
        cls, annotation: Any, required: bool = True
    ) -> Optional["OneOf"]:
        if annotation.__origin__ == Literal:
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
            allowed_values = ", ".join(self.allowed_values)
            raise ValidationError(
                f"value `{value}` not allowed; allowed values are `{allowed_values}`"
            )


class Dictionary(Field):
    @classmethod
    def from_annotation(
        cls, annotation: Any, required: bool = True
    ) -> Optional["Dictionary"]:
        if annotation.__origin__ == dict:
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

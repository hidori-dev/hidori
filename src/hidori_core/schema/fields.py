from typing import Any, Optional, Tuple

from hidori_core.compat.typing import Literal
from hidori_core.schema.base import Field, ValidationError


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

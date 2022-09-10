from typing import Any, Literal, Optional

from hidori_core.schema.base import Field, ValidationError


class Text(Field):
    @classmethod
    def from_annotation(cls, annotation: Any, required: bool = True) -> Optional["Text"]:
        if annotation == str:
            return cls(required)
    
    def __init__(self, required: bool) -> None:
        self.required = required


class OneOf(Field):
    @classmethod
    def from_annotation(cls, annotation: Any, required: bool = True) -> Optional["OneOf"]:
        if annotation.__origin__ == Literal:
            return cls(annotation.__args__, required)

    def __init__(self, values: tuple[Any], required: bool) -> None:
        self.allowed_values = values
        self.required = required

    def validate(self, value: Optional[Any]) -> Optional[Any]:
        super().validate(value)

        if value in self.allowed_values:
            return value
        else:
            allowed_values = ", ".join(self.allowed_values)
            raise ValidationError(
                f"value `{value}` is not allowed. Allowed values: {allowed_values}"
            )

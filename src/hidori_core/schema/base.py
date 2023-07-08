from typing import Any, Dict, List, Optional, Type, TypeVar, Union, get_origin

try:
    from types import UnionType
except ImportError:
    # Compatibility with Python < 3.10
    UnionType = Union  # type: ignore

from hidori_core.schema.errors import (
    ConstraintError,
    SchemaError,
    SkipFieldError,
    ValidationError,
)

TField = TypeVar("TField", bound="Field")

FIELDS_REGISTRY: List[Type["Field"]] = []


class Field:
    required: bool

    def __init_subclass__(cls) -> None:
        FIELDS_REGISTRY.append(cls)

    @classmethod
    def from_annotation(
        cls: Type[TField], annotation: Any, required: bool = True
    ) -> Optional[TField]:
        ...

    def validate(self, value: Optional[Any]) -> None:
        if self.required and not value:
            raise ValidationError("value for required field not provided")
        elif self.required is False and not value:
            raise SkipFieldError()


class Constraint:
    def process_schema(self, annotations: Dict[str, Any]) -> None:
        ...

    def apply(self, schema: "Schema", data: Dict[str, Any]) -> None:
        ...


class Schema:
    fields: Dict[str, Field]

    def __init_subclass__(cls) -> None:
        cls.fields = {}
        errors = {}

        for name, annotation in cls.__annotations__.items():
            if name == "fields":
                continue

            constraint = getattr(cls, name, None)
            if constraint and isinstance(constraint, Constraint):
                try:
                    constraint.process_schema(cls.__annotations__)
                except ConstraintError as e:
                    errors[name] = str(e)
                    continue

            cls.fields[name] = field_from_annotation(annotation)

        if errors:
            raise SchemaError(errors)

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        errors = {}

        for name, field in self.fields.items():
            constraint = getattr(self, name, None)
            if constraint and isinstance(constraint, Constraint):
                constraint.apply(self, data)

            try:
                # TODO: No such field provided in data
                field_data = data.get(name)
                field.validate(field_data)
            except ValidationError as e:
                errors[name] = str(e)
                continue
            except SchemaError as e:
                errors[name] = e.errors
            except SkipFieldError:
                continue

        if errors:
            raise SchemaError(errors)

        return data


def field_from_annotation(annotation: Any, required: bool = True) -> Field:
    origin = get_origin(annotation)
    if origin in [Union, UnionType]:
        assert len(annotation.__args__) == 2
        assert any([isinstance(None, ty) for ty in annotation.__args__])

        for ty in annotation.__args__:
            if isinstance(None, ty):
                continue

            return field_from_annotation(ty, required=False)

    for field_cls in FIELDS_REGISTRY:
        field = field_cls.from_annotation(annotation, required)
        if field is not None:
            return field

    raise RuntimeError("internal error")

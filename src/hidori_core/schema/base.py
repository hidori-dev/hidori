from typing import Any, Dict, List, Optional, Type, TypeVar, Union

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

    def validate(self, value: Optional[Any]) -> Optional[Any]:
        if self.required and not value:
            raise ValidationError("value for required field not provided")
        elif self.required is False and not value:
            raise SkipFieldError()
        else:
            return value


class Constraint:
    def process_schema(self, annotations: Dict[str, Any]) -> None:
        ...

    def apply(self, schema: "Schema", data: Dict[str, Any]) -> None:
        ...


class Schema:
    # TODO: Add support for sub-schemas (especially for PipelineSchema)
    fields: Dict[str, Field]

    def __init_subclass__(cls):
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
        validated_data: Dict[str, Any] = {}
        errors = {}

        for name, field in self.fields.items():
            constraint = getattr(self, name, None)
            if constraint and isinstance(constraint, Constraint):
                constraint.apply(self, data)

            try:
                # TODO: No such field provided in data
                field_data = data.get(name)
                field.validate(field_data)
                validated_data[name] = field_data
            except ValidationError as e:
                errors[name] = str(e)
                continue
            except SkipFieldError:
                continue

        if errors:
            raise SchemaError(errors)

        return validated_data


def field_from_annotation(annotation: Any, required: bool = True) -> Field:
    for field_cls in FIELDS_REGISTRY:
        field = field_cls.from_annotation(annotation, required)
        if field is not None:
            return field

    if annotation.__origin__ == Union:
        # TODO: Impl unions other than Optional when necessary
        assert len(annotation.__args__) == 2

        required = False
        for base_type in annotation.__args__:
            if isinstance(None, base_type):
                continue

            return field_from_annotation(base_type, required)

    # TODO: Finish impl for other cases
    raise RuntimeError("internal error")

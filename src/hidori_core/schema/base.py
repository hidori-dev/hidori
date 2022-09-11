from typing import Any, List, Optional, Type, TypeVar, Union

from hidori_core.schema.errors import SchemaError, SkipFieldError, ValidationError

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


class Schema:
    fields: dict[str, Field]

    def __init_subclass__(cls):
        cls.fields = {}

        for name, annotation in cls.__annotations__.items():
            if name == "fields":
                continue
            cls.fields[name] = field_from_annotation(annotation)

    @classmethod
    def validate(cls, data: dict) -> dict:
        validated_data = {}
        errors = {}

        for name, field in cls.fields.items():
            try:
                validated_data[name] = field.validate(data.get(name))
            except ValidationError as e:
                errors[name] = str(e)
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

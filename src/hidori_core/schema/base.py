from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union, get_origin

try:
    from types import UnionType
except ImportError:
    # Compatibility with Python < 3.10
    UnionType = Union  # type: ignore

from hidori_core.schema.errors import (
    ModifierError,
    SchemaError,
    SkipFieldError,
    ValidationError,
)

TField = TypeVar("TField", bound="Field")

FIELDS_REGISTRY: List[Type["Field"]] = []

_sentinel = object()

DataCondtion = Callable[[Dict[str, Any]], bool]


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
        if self.required and value is _sentinel:
            raise ValidationError("value for required field not provided")
        elif self.required is False and value is _sentinel:
            raise SkipFieldError()


class SchemaModifier:
    data_conditions: List[DataCondtion]

    def process_schema(self, annotations: Dict[str, Any]) -> None:
        ...

    def apply(self, schema: "Schema", data: Dict[str, Any]) -> None:
        for condition in self.data_conditions:
            if not condition(data):
                return

        self.apply_to_schema(schema, data)

    def apply_to_schema(self, schema: "Schema", data: Dict[str, Any]) -> None:
        ...


class Definition:
    def __init__(
        self,
        modifiers: Optional[List[SchemaModifier]] = None,
        default: Any = _sentinel,
        default_factory: Optional[Callable[[], Any]] = None,
    ) -> None:
        if default is not _sentinel and default_factory is not None:
            raise RuntimeError("provide either default value or default factory")

        self.modifiers = modifiers or []
        self.default = default
        self.default_factory = default_factory
        self._field_name: Optional[str] = None
        self._errors: List[str] = []

    @property
    def errors(self) -> List[str]:
        return self._errors

    def assign_field_name(self, field_name: str) -> None:
        self._field_name = field_name

    def validate_modifiers(self, annotations: Dict[str, Any]) -> None:
        for modifier in self.modifiers:
            try:
                modifier.process_schema(annotations)
            except ModifierError as e:
                self._errors.append(str(e))

    def apply_modifiers(self, schema: "Schema", data: Dict[str, Any]) -> None:
        for modifier in self.modifiers:
            if self._field_name in data:
                modifier.apply(schema, data)

    def apply_default(self, data: Dict[str, Any]) -> None:
        assert self._field_name
        if self.default is not _sentinel:
            data[self._field_name] = data.get(self._field_name, self.default)
        elif self.default_factory is not None:
            data[self._field_name] = data.get(self._field_name, self.default_factory())


def define(
    modifiers: Optional[List[SchemaModifier]] = None,
    default: Optional[Any] = _sentinel,
    default_factory: Optional[Callable[[], Any]] = None,
) -> Any:
    return Definition(modifiers, default, default_factory)


class Schema:
    fields: Dict[str, Field]

    def __init_subclass__(cls) -> None:
        cls.fields = {}
        errors = {}

        for name, annotation in cls.__annotations__.items():
            if name == "fields":
                continue

            # If a definition is provided, validate the modifiers against the
            # provided annotations. For example, the RequiresModifier needs
            # to ensure that the required fields exist in the schema.
            definition = getattr(cls, name, _sentinel)
            if isinstance(definition, Definition):
                definition.assign_field_name(name)
                definition.validate_modifiers(cls.__annotations__)
                if definition.errors:
                    errors[name] = definition.errors
                    continue
            # Assume that user provided a value to be used as a default.
            elif definition is not _sentinel:
                field_definition = Definition(default=definition)
                field_definition.assign_field_name(name)
                setattr(cls, name, field_definition)

            cls.fields[name] = field_from_annotation(annotation)

        if errors:
            raise SchemaError(errors)

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        errors: Dict[str, Any] = {}

        for name, field in self.fields.items():
            definition = getattr(self, name, None)
            if isinstance(definition, Definition):
                definition.apply_modifiers(self, data)
                definition.apply_default(data)

            try:
                field_data = data.get(name, _sentinel)
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

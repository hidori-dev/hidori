import abc
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union, get_origin

try:
    from types import UnionType
except ImportError:
    # Compatibility with Python < 3.10
    UnionType = Union  # type: ignore

from hidori_core.schema import errors as schema_errors

TField = TypeVar("TField", bound="Field")

FIELDS_REGISTRY: List[Type["Field"]] = []

_sentinel = object()

DataCondtion = Callable[[Dict[str, Any]], bool]


class Field(abc.ABC):
    required: bool

    def __init_subclass__(cls) -> None:
        FIELDS_REGISTRY.append(cls)

    @classmethod
    @abc.abstractmethod
    def from_annotation(
        cls: Type[TField], annotation: Any, required: bool = True
    ) -> Optional[TField]:
        raise NotImplementedError()

    def validate(self, value: Any) -> Any:
        if self.required and value is _sentinel:
            raise schema_errors.ValidationError("value for required field not provided")
        elif self.required is False and value is _sentinel:
            raise schema_errors.SkipFieldError()


class SchemaModifier(abc.ABC):
    data_conditions: List[DataCondtion]

    @abc.abstractmethod
    def process_schema(self, annotations: Dict[str, Any]) -> None:
        raise NotImplementedError()

    def apply(self, schema: "Schema", data: Dict[str, Any]) -> None:
        for condition in self.data_conditions:
            if not condition(data):
                return

        self.apply_to_schema(schema, data)

    @abc.abstractmethod
    def apply_to_schema(self, schema: "Schema", data: Dict[str, Any]) -> None:
        raise NotImplementedError()


class Definition:
    def __init__(
        self,
        modifiers: Optional[List[SchemaModifier]] = None,
        default: Any = _sentinel,
        default_factory: Optional[Callable[[], Any]] = None,
    ) -> None:
        if default is not _sentinel and default_factory is not None:
            raise schema_errors.MultipleDefaultMethodsError(
                "provide either default value or default factory"
            )

        self.modifiers = modifiers or []
        self.default = default
        self.default_factory = default_factory
        self._field_name: Optional[str] = None
        self._errors: List[str] = []

    @property
    def errors(self) -> List[str]:
        return self._errors

    @property
    def field_name(self) -> Optional[str]:
        return self._field_name

    @field_name.setter
    def field_name(self, value: str) -> None:
        if self.field_name is not None:
            raise schema_errors.DefinitionAlreadyAssigned(
                f"cannot change field name {self.field_name} for definition"
            )
        self._field_name = value

    def validate_modifiers(self, annotations: Dict[str, Any]) -> None:
        for modifier in self.modifiers:
            try:
                modifier.process_schema(annotations)
            except schema_errors.ModifierError as e:
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
    _internals_fields: Dict[str, Field]

    def __init_subclass__(cls) -> None:
        for name in cls.__annotations__.keys():
            if name.startswith("_internals"):
                raise schema_errors.FieldNameNotAllowed(
                    "_internals prefix is reserved for internal use"
                )

        cls._internals_fields = {}
        errors = {}

        for name, annotation in cls.__annotations__.items():
            # If a definition is provided, validate the modifiers against the
            # provided annotations. For example, the RequiresModifier needs
            # to ensure that the required fields exist in the schema.
            definition = getattr(cls, name, _sentinel)
            if isinstance(definition, Definition):
                definition.field_name = name
                definition.validate_modifiers(cls.__annotations__)
                if definition.errors:
                    errors[name] = definition.errors
                    continue
            # Assume that user provided a value to be used as a default.
            elif definition is not _sentinel:
                field_definition = Definition(default=definition)
                field_definition.field_name = name
                setattr(cls, name, field_definition)

            cls._internals_fields[name] = field_from_annotation(annotation)

        if errors:
            raise schema_errors.SchemaError(errors)

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        errors: Dict[str, Any] = {}
        validated_data: Dict[str, Any] = {}

        for name, field in self._internals_fields.items():
            definition = getattr(self, name, None)
            if isinstance(definition, Definition):
                definition.apply_modifiers(self, data)
                definition.apply_default(data)

            try:
                field_data = data.get(name, _sentinel)
                validated_data[name] = field.validate(field_data)
            except schema_errors.ValidationError as e:
                errors[name] = str(e)
                continue
            except schema_errors.SchemaError as e:
                errors[name] = e.errors
            except schema_errors.SkipFieldError:
                continue

        if errors:
            raise schema_errors.SchemaError(errors)

        return validated_data


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

    raise schema_errors.UnrecognizedFieldType(
        f"could not determine schema field for {annotation.__name__} type"
    )

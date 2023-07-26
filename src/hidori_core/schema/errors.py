from typing import Any, Dict


class MultipleDefaultMethodsError(Exception):
    ...


class DefinitionAlreadyAssigned(Exception):
    ...


class FieldNameNotAllowed(Exception):
    ...


class UnrecognizedFieldType(Exception):
    ...


class ValidationError(Exception):
    ...


class ModifierError(Exception):
    ...


class SkipFieldError(Exception):
    ...


class SchemaError(Exception):
    def __init__(self, errors: Dict[str, Any]) -> None:
        self.errors = errors
        super().__init__(str(errors))

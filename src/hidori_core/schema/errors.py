from typing import Any, Dict


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

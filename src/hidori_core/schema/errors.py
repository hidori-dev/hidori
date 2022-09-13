from typing import Dict


class ValidationError(Exception):
    ...


class ConstraintError(Exception):
    ...


class SkipFieldError(Exception):
    ...


class SchemaError(Exception):
    def __init__(self, errors: Dict[str, str]) -> None:
        self.errors = errors
        super().__init__(str(errors))

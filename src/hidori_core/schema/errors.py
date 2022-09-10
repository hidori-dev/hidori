class ValidationError(Exception):
    ...


class SkipFieldError(Exception):
    ...


class SchemaError(Exception):
    def __init__(self, errors: dict[str, str]) -> None:
        super().__init__()
        self.errors = errors

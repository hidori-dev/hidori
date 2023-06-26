import argparse
from typing import Any, Mapping

NATIVE_FIELDS_BY_FIELD_NAME: dict[str, type["Field"]] = {}


class Field:
    action: str | type[argparse.Action]

    def __init_subclass__(cls, field_name: str | None = None) -> None:
        if field_name is not None:
            assert field_name not in NATIVE_FIELDS_BY_FIELD_NAME
            NATIVE_FIELDS_BY_FIELD_NAME[field_name] = cls

    @classmethod
    def add_to_parser(
        cls, parser_obj: argparse.ArgumentParser, field_metadata: Mapping[str, Any]
    ) -> None:
        ...

    @classmethod
    def prepare_kwargs(cls, field_metadata: Mapping[str, Any]) -> dict[str, Any]:
        kwargs = {}
        help_text = field_metadata.get("help")
        if help_text is not None:
            kwargs["help"] = help_text
        return kwargs

import argparse
from typing import Any, Mapping

NATIVE_FIELDS_BY_FIELD_NAME: dict[str, type["Field"]] = {}
NATIVE_FIELDS_BY_FIELD_TYPE: dict[Any, type["Field"]] = {}


def get_native_field_by_name_or_type(
    field_name: str, field_type: Any
) -> type["Field"] | None:
    return NATIVE_FIELDS_BY_FIELD_NAME.get(
        field_name
    ) or NATIVE_FIELDS_BY_FIELD_TYPE.get(field_type)


class Field:
    action: str | type[argparse.Action]

    def __init_subclass__(
        cls, field_name: str | None = None, field_type: Any = None
    ) -> None:
        # Either field_name or field_type must be provided
        assert (not field_name) ^ (not field_type)

        if field_name is not None:
            assert field_name not in NATIVE_FIELDS_BY_FIELD_NAME
            NATIVE_FIELDS_BY_FIELD_NAME[field_name] = cls
        elif field_type is not None:
            assert field_name not in NATIVE_FIELDS_BY_FIELD_TYPE
            NATIVE_FIELDS_BY_FIELD_TYPE[field_type] = cls

    @classmethod
    def add_to_parser(
        cls,
        parser_obj: argparse.ArgumentParser,
        field_name: str,
        field_metadata: Mapping[str, Any],
    ) -> None:
        ...

    @classmethod
    def prepare_kwargs(cls, field_metadata: Mapping[str, Any]) -> dict[str, Any]:
        kwargs = {}
        help_text = field_metadata.get("help")
        if help_text is not None:
            kwargs["help"] = help_text
        return kwargs

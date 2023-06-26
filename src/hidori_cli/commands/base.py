from __future__ import annotations

import argparse
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from hidori_cli.fields import NATIVE_FIELDS_BY_FIELD_NAME

TD = TypeVar("TD", bound="BaseData")

BASE_COMMAND_NAME = "base"
COMMAND_REGISTRY: defaultdict[str, dict[str, type[Command[Any]]]] = defaultdict(dict)


@dataclass
class BaseData:
    subparser_name: str


class Command(Generic[TD]):
    name: str
    data_cls: type[TD]

    def __init_subclass__(cls) -> None:
        name_parts: list[str] = re.findall(".[^A-Z]*", cls.__name__)
        if len(name_parts) == 2:
            app_name, cmd_name = name_parts[0], BASE_COMMAND_NAME
        else:
            app_name, cmd_name = name_parts[0], name_parts[1]
        app_name = f"hidori-{app_name.lower()}"
        cmd_name = cmd_name.lower()

        if cmd_name in COMMAND_REGISTRY[app_name]:
            raise RuntimeError(
                f"command {cmd_name} is already defined for app {app_name}"
            )
        cls.name = cmd_name
        COMMAND_REGISTRY[app_name][cmd_name] = cls

    def __init__(self, parser_obj: argparse.ArgumentParser) -> None:
        for field_name, field in self.data_cls.__dataclass_fields__.items():
            if field_name == "subparser_name":
                continue

            kwargs = {}
            help_text = field.metadata.get("help")
            is_positional = field.metadata.get("is_positional", True)
            if help_text:
                kwargs["help"] = help_text

            field_cls = NATIVE_FIELDS_BY_FIELD_NAME.get(field_name)
            if field_cls:
                field_cls.add_to_parser(parser_obj, field.metadata)
                continue

            if field.type in (bool, "bool"):
                parser_obj.add_argument(
                    f"--{field.name}", action="store_true", **kwargs
                )

            if field.type in (str, "str"):
                name = field.name if is_positional else f"--{field_name}"
                parser_obj.add_argument(name, type=str, **kwargs)

    def run(self, parser_data: dict[str, Any]) -> None:
        cmd_data = {k: parser_data[k] for k in self.data_cls.__dataclass_fields__}
        data_obj = self.data_cls(**cmd_data)
        self.execute(data_obj)

    def execute(self, data: TD) -> None:
        ...

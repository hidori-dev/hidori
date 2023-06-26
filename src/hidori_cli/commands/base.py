from __future__ import annotations

import argparse
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from hidori_cli.fields import get_native_field_by_name_or_type

TD = TypeVar("TD", bound="BaseData")

BASE_COMMAND_NAME = "base"
COMMAND_REGISTRY: defaultdict[str, dict[str, type[Command[Any]]]] = defaultdict(dict)


@dataclass
class BaseData:
    subparser_name: str | None


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

            field_cls = get_native_field_by_name_or_type(field_name, field.type)
            if field_cls is None:
                raise RuntimeError(
                    f"unable to find native field for field name {field_name} "
                    f"and type {field.type}"
                )
            field_cls.add_to_parser(parser_obj, field_name, field.metadata)

    def run(self, parser_data: dict[str, Any]) -> None:
        cmd_data = {k: parser_data.get(k) for k in self.data_cls.__dataclass_fields__}
        data_obj = self.data_cls(**cmd_data)
        self.execute(data_obj)

    def execute(self, data: TD) -> None:
        ...

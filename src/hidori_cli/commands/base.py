from __future__ import annotations

import argparse
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

TD = TypeVar("TD", bound="BaseData")

COMMAND_REGISTRY: defaultdict[str, dict[str, type[Command[Any]]]] = defaultdict(dict)


@dataclass
class BaseData:
    subparser_name: str


class Command(Generic[TD]):
    name: str
    data_cls: type[TD]
    backend_parse_content: bool = False

    def __init_subclass__(cls) -> None:
        app_name, cmd_name, _ = re.findall(".[^A-Z]*", cls.__name__)
        app_name = f"hidori-{app_name.lower()}"
        cmd_name = cmd_name.lower()

        if cmd_name in COMMAND_REGISTRY:
            raise RuntimeError()
        cls.name = cmd_name
        COMMAND_REGISTRY[app_name][cmd_name] = cls

    def __init__(self, subparser: argparse.ArgumentParser) -> None:
        for field_name, field in self.data_cls.__dataclass_fields__.items():
            if field_name == "subparser_name":
                continue

            kwargs = {}
            help_text = field.metadata.get("help", "")
            is_positional = field.metadata.get("is_positional", True)
            if help_text:
                kwargs["help"] = help_text

            if field.type in (bool, "bool"):
                subparser.add_argument(f"--{field.name}", action="store_true", **kwargs)

            if field.type in (str, "str"):
                name = field.name if is_positional else f"--{field_name}"
                subparser.add_argument(name, type=str, **kwargs)

    def execute(self, data: TD) -> None:
        ...

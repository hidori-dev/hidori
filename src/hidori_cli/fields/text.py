import argparse
from typing import Any, Mapping

from hidori_cli.fields.base import Field


class TextField(Field, field_type=str):
    @classmethod
    def add_to_parser(
        cls,
        parser_obj: argparse.ArgumentParser,
        field_name: str,
        field_metadata: Mapping[str, Any],
    ) -> None:
        is_positional = field_metadata.get("is_positional", True)
        name = field_name if is_positional else f"--{field_name}"
        parser_obj.add_argument(
            name,
            type=str,
            **cls.prepare_kwargs(field_metadata),
        )

import argparse
from typing import Any, Mapping

from hidori_cli.fields.base import Field


class BooleanField(Field, field_type=bool):
    @classmethod
    def add_to_parser(
        cls,
        parser_obj: argparse.ArgumentParser,
        field_name: str,
        field_metadata: Mapping[str, Any],
    ) -> None:
        parser_obj.add_argument(
            f"--{field_name}",
            action="store_true",
            **cls.prepare_kwargs(field_metadata),
        )

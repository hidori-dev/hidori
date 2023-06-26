import argparse
from typing import Any, Mapping

from hidori_cli.fields.base import Field


class ExtraDataField(Field, field_name="extra_data"):
    @classmethod
    def add_to_parser(
        cls,
        parser_obj: argparse.ArgumentParser,
        field_name: str,
        field_metadata: Mapping[str, Any],
    ) -> None:
        parser_obj.add_argument(
            "extra_data",
            nargs=argparse.REMAINDER,
            **cls.prepare_kwargs(field_metadata),
        )

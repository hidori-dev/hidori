import argparse
from typing import Any

from hidori_cli.fields.base import Field
from hidori_common.cli import get_version


class VersionField(Field, field_name="version"):
    @classmethod
    def add_to_parser(
        cls, parser_obj: argparse.ArgumentParser, field_metadata: dict[str, Any]
    ) -> None:
        parser_obj.add_argument(
            "-V",
            "--version",
            action="version",
            version=f"%(prog)s {get_version()}",
            **cls.prepare_kwargs(field_metadata),
        )

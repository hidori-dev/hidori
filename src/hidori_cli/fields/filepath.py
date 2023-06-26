import argparse
import pathlib
from typing import Any, Mapping, Sequence

from hidori_cli.fields.base import Field


class FilePathAction(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str | Sequence[str] | None,
        option_string: str | None = None,
    ) -> None:
        if not values:
            return

        values = [values] if isinstance(values, str) else values
        if len(values) > 1:
            msg = "filepath field accepts a single value only"
            raise argparse.ArgumentError(self, msg)

        filepath = pathlib.Path(values[0])
        if not filepath.exists() or not filepath.is_file():
            msg = f"unable to access file: {filepath}"
            raise argparse.ArgumentError(self, msg)

        setattr(namespace, self.dest, filepath)


class FilePathField(Field, field_type=pathlib.Path):
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
            action=FilePathAction,
            **cls.prepare_kwargs(field_metadata),
        )

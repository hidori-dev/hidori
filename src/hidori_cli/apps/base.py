import argparse
import re

from hidori_cli.commands import COMMAND_REGISTRY, Command
from hidori_cli.commands.base import BASE_COMMAND_NAME, BaseData


class BaseCLIApplication:
    def __init__(self) -> None:
        name_parts: list[str] = re.findall(".[^A-Z]*", type(self).__name__)[:-1]
        self.name = "-".join([p.lower() for p in name_parts])
        self.parser = argparse.ArgumentParser(description=self.__doc__)
        self._commands: dict[str, Command[BaseData]] = {}
        self._register_commands()

    def _register_commands(self) -> None:
        subparsers = self.parser.add_subparsers(dest="subparser_name")
        for command_cls in COMMAND_REGISTRY[self.name].values():
            parser_obj = (
                self.parser
                if command_cls.name == BASE_COMMAND_NAME
                else subparsers.add_parser(command_cls.name, help=command_cls.__doc__)
            )
            self._commands[command_cls.name] = command_cls(parser_obj)

    def run(self) -> None:
        parser_data = self.parser.parse_args()
        command_name: str = parser_data.subparser_name or BASE_COMMAND_NAME
        command = self._commands[command_name]
        command.run(parser_data.__dict__)

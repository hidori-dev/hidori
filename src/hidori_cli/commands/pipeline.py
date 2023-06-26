from dataclasses import dataclass, field

from hidori_cli.commands.base import BaseData, Command


@dataclass
class PipelineData(BaseData):
    version: bool = field(metadata={"help": "Show the installed version and exit."})


class PipelineCommand(Command[PipelineData]):
    """pipeline command"""

    data_cls = PipelineData

    def execute(self, data: PipelineData) -> None:
        ...

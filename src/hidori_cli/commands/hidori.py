from dataclasses import dataclass, field

import hidori_core
from hidori_cli.commands.base import BaseData, Command


@dataclass
class HidoriData(BaseData):
    version: bool = field(metadata={"help": "Show the installed version and exit."})


class HidoriCommand(Command[HidoriData]):
    """hidori command"""

    data_cls = HidoriData

    def execute(self, data: HidoriData) -> None:
        if data.version:
            print(hidori_core.__version__)

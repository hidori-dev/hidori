import uuid
from dataclasses import dataclass, field

from hidori_cli.commands.base import BaseData, Command
from hidori_common import ConsolePrinter
from hidori_runner.drivers import create_driver


@dataclass
class HidoriData(BaseData):
    destination: str = field(
        metadata={"help": "user and target information, e.g. user@host"}
    )
    module: str = field(metadata={"help": "module to be executed"})
    extra_data: list[str] = field(metadata={"help": "module data if any"})
    version: bool = field(
        default=False, metadata={"help": "show the installed version and exit"}
    )


class HidoriCommand(Command[HidoriData]):
    """hidori command"""

    data_cls = HidoriData

    def execute(self, data: HidoriData) -> None:
        user, target = data.destination.split("@")

        printer = ConsolePrinter(user=user, target=target)
        driver = create_driver({"user": user, "target": target})
        extra_data = {}
        for entry in data.extra_data:
            name, value = entry.split("=")
            extra_data[name] = value

        task_id = uuid.uuid4().hex
        exchange = driver.prepare_call(
            task_id=task_id,
            task_json={"name": "Call", "data": {"module": data.module, **extra_data}},
        )
        driver.finalize(exchange)
        driver.invoke_executor(exchange, task_id)
        printer.print_all(exchange.messages)
        exchange.messages.clear()

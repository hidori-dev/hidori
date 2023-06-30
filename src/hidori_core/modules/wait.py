import time
from typing import Dict

from hidori_core.modules.base import Module
from hidori_core.schema import Schema
from hidori_core.utils import Messenger


class WaitSchema(Schema):
    seconds: str


class WaitModule(Module, name="wait", schema_cls=WaitSchema):
    def execute(self, validated_data: Dict[str, str], messenger: Messenger) -> None:
        seconds = int(validated_data["seconds"])
        time.sleep(seconds)
        messenger.queue_success(f"Successfuly waited for {seconds} seconds")

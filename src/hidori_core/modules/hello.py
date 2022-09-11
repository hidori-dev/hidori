import os

from hidori_core.modules.base import Module
from hidori_core.schema import Schema
from hidori_core.utils.messenger import Messenger


class HelloSchema(Schema):
    ...


class HelloModule(Module, name="hello", schema_cls=HelloSchema):
    def execute(self, validated_data, messenger: Messenger):
        uname_result = os.uname()
        messenger.queue_success(
            f"Hello from {uname_result.sysname} {uname_result.nodename} "
            f"{uname_result.release}"
        )
        return {"state": "unaffected"}
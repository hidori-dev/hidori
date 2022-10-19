import os
import shutil

import pytest

from hidori_common.typings import Transport
from hidori_core.modules import MODULES_REGISTRY
from hidori_core.modules.base import Module
from hidori_core.schema.base import Schema
from hidori_core.utils.messenger import Messenger
from hidori_runner.transports.utils import get_messages


class ExampleSchema(Schema):
    action: str


class ExampleModule(Module, name="example", schema_cls=ExampleSchema):
    def execute(self, validated_data: dict[str, str], messenger: Messenger) -> None:
        if validated_data["action"] == "error":
            messenger.queue_error("runtime error")
            raise RuntimeError()

        messenger.queue_success("ok")


class ExampleDriver:
    ...


class ExampleTransport(Transport[ExampleDriver], name="example"):
    def push(self, source: str, dest: str) -> list[dict[str, str]]:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        try:
            shutil.copy(source, dest)
        except FileNotFoundError:
            return get_messages("file not found", self.name)
        except PermissionError:
            return get_messages("no permission", self.name)

        return []

    def invoke(self, path: str, args: list[str]) -> list[dict[str, str]]:
        try:
            with open(path) as f:
                out = f.read()
        except FileNotFoundError:
            return get_messages("file not found", self.name)
        except PermissionError:
            return get_messages("no permission", self.name)

        for arg in args:
            out: str = getattr(out, arg)()
        return [{"type": "success", "task": "example", "message": out}]


@pytest.fixture(scope="session")
def example_transport():
    return ExampleTransport(ExampleDriver())


@pytest.fixture(scope="session")
def example_messenger():
    return Messenger("example")


@pytest.fixture(scope="session")
def example_module():
    return MODULES_REGISTRY["example"]

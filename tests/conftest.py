import os
import pathlib
import shutil

import pytest

from hidori_common.typings import Transport
from hidori_core.modules import MODULES_REGISTRY
from hidori_core.modules.base import Module
from hidori_core.schema.base import Schema
from hidori_core.utils.messenger import Messenger
from hidori_runner.drivers.base import Driver
from hidori_runner.transports.utils import get_messages


class ExampleSchema(Schema):
    action: str


class ExampleDriverSchema(Schema):
    value: str


class ExampleModule(Module, name="example", schema_cls=ExampleSchema):
    def execute(self, validated_data: dict[str, str], messenger: Messenger) -> None:
        if validated_data["action"] == "error":
            messenger.queue_error("runtime error")
            raise RuntimeError()

        messenger.queue_success("ok")


class ExampleTransport(Transport["ExampleDriver"], name="example"):
    def get_destination(self, source: str) -> str:
        return str(pathlib.Path("/example") / pathlib.Path(source).name)

    def push(self, source: str) -> list[dict[str, str]]:
        dest = self.get_destination(source)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        try:
            shutil.copy(source, dest)
        except FileNotFoundError:
            return get_messages("file not found", self.name, require_json=False)
        except PermissionError:
            return get_messages("no permission", self.name, require_json=False)

        return []

    def invoke(self, path: str, args: list[str]) -> list[dict[str, str]]:
        try:
            with open(path) as f:
                out = f.read()
        except FileNotFoundError:
            return get_messages("file not found", self.name, require_json=False)
        except PermissionError:
            return get_messages("no permission", self.name, require_json=False)

        for arg in args:
            out: str = getattr(out, arg)()
        out += f"-{self._driver.value}"
        return [{"type": "success", "task": "example", "message": out}]


class ExampleDriver(Driver, name="example"):
    schema = ExampleDriverSchema()
    transport_cls = ExampleTransport

    def __init__(self, config: dict[str, str]) -> None:
        super().__init__(config)
        self.value = config["value"]

    @property
    def user(self) -> str:
        return "example-user"

    @property
    def target_id(self) -> str:
        return "example-target"


@pytest.fixture(scope="session")
def example_driver_cls():
    return ExampleDriver


@pytest.fixture(scope="session")
def example_driver():
    return ExampleDriver(config={"value": "42"})


@pytest.fixture(scope="session")
def example_transport(example_driver: ExampleDriver):
    return ExampleTransport(example_driver)


@pytest.fixture(scope="session")
def example_messenger():
    return Messenger("example")


@pytest.fixture(scope="session")
def example_module():
    return MODULES_REGISTRY["example"]

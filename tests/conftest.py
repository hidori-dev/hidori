import importlib
import os
import pathlib
import shutil
from unittest.mock import Mock, patch

import pytest

from hidori_common.dirs import get_user_cache_path
from hidori_common.typings import Transport
from hidori_core.modules import MODULES_REGISTRY
from hidori_core.modules.base import Module
from hidori_core.schema.base import Schema
from hidori_core.utils.messenger import Messenger
from hidori_pipelines.pipeline import Pipeline, TargetData
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


@pytest.fixture(scope="session")
def example_pipeline(example_driver: ExampleDriver):
    target_data: TargetData = {"target": "example", "driver": example_driver}
    tasks_data = {"Hello world": {"module": "hello"}}
    return Pipeline(target_data, tasks_data)


@pytest.fixture(scope="function")
def mock_uuid():
    with patch("uuid.uuid4", return_value=Mock(hex=42)):
        yield


@pytest.fixture(scope="function")
def setup_filesystem(fs):
    get_user_cache_path().mkdir(parents=True, exist_ok=False)

    # TODO: remove typing-extensions setup when py37 drops
    ty_exts_mod = importlib.import_module("typing_extensions")
    pathlib.Path(ty_exts_mod.__file__).parent.mkdir(parents=True, exist_ok=False)
    with open(ty_exts_mod.__file__, "w"):
        ...

    core_mod = importlib.import_module("hidori_core")
    pathlib.Path(core_mod.__path__[0]).mkdir(parents=True, exist_ok=False)

    runner_mod = importlib.import_module("hidori_runner")
    executor_path = pathlib.Path(runner_mod.__path__[0]) / "executors/remote.py"
    pathlib.Path(executor_path).parent.mkdir(parents=True, exist_ok=False)
    with open(executor_path, "w"):
        ...

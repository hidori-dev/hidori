import abc
import dataclasses
import importlib
import json
import pathlib
import shutil
from typing import Any, Self

from hidori_common.typings import Pipeline, Transport
from hidori_core.schema.base import Schema
from hidori_runner.drivers.utils import create_pipeline_dir

DEFAULT_DRIVER = "ssh"

DRIVERS_REGISTRY: dict[str, type["Driver"]] = {}


@dataclasses.dataclass
class PreparedPipeline:
    localpath: pathlib.Path
    transport: Transport[Any]
    messages: list[dict[str, str]] = dataclasses.field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any([m["type"] == "error" for m in self.messages])


class Driver:
    schema: Schema
    transport_cls: type[Transport[Self]]

    def __init_subclass__(cls, *, name: str) -> None:
        super().__init_subclass__()

        if name in DRIVERS_REGISTRY:
            raise RuntimeError(f"{name} driver is already registered.")

        # TODO: seems like mypy doesn't recognize the @abstractmethod
        if cls.user.__isabstractmethod__:  # type: ignore
            raise NotImplementedError(
                f"user property is not implemented in the driver {name}"
            )
        if cls.target_id.__isabstractmethod__:  # type: ignore
            raise NotImplementedError(
                f"target_id property is not implemented in the driver {name}"
            )
        # TODO: Verify that transport_cls matches the Transport protocol
        DRIVERS_REGISTRY[name] = cls

    def __init__(self, config: Any) -> None:
        self.schema.validate(config)

    @property
    @abc.abstractmethod
    def user(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def target_id(self) -> str:
        ...

    def prepare(self: Self, pipeline: Pipeline) -> PreparedPipeline:
        localpath = create_pipeline_dir(self.target_id)
        self.prepare_modules(localpath)
        self.prepare_executor(localpath)
        self.prepare_tasks(localpath, pipeline)
        return PreparedPipeline(localpath=localpath, transport=self.transport_cls(self))

    def finalize(self, prepared_pipeline: PreparedPipeline) -> None:
        transport = prepared_pipeline.transport
        source = str(prepared_pipeline.localpath)
        prepared_pipeline.messages.extend(transport.push(source))

    def invoke_executor(
        self, prepared_pipeline: PreparedPipeline, task_id: str
    ) -> None:
        transport = prepared_pipeline.transport
        prepared_pipeline.messages.extend(transport.invoke("executor.py", [task_id]))

    def prepare_modules(self, localpath: pathlib.Path) -> None:
        # TODO: Driver should only pick required modules.
        # Use MODULES_REGISTRY and delivered modules for that
        # It will also allow third parties to define their own modules.
        # TODO: This (copying typing-extensions) is terrible.
        # Delete as soon as 3.7 drops.
        import typing_extensions

        ty_exts_path = typing_extensions.__file__
        tmp_ty_exts_path = localpath / "typing_extensions.py"
        shutil.copyfile(ty_exts_path, tmp_ty_exts_path)
        self._copy_core_tree(localpath / "hidori_core")

    def prepare_executor(self, localpath: pathlib.Path) -> None:
        # TODO: Use appropriate executor instead of a hardcoded remote
        runner_module = importlib.import_module("hidori_runner")
        executor_path = pathlib.Path(runner_module.__path__[0]) / "executors/remote.py"
        shutil.copyfile(executor_path, localpath / "executor.py")

    def prepare_tasks(self, localpath: pathlib.Path, pipeline: Pipeline) -> None:
        for step in pipeline.steps:
            local_task_path = localpath / f"task-{step.task_id}.json"
            with open(local_task_path, "w") as task_file:
                json.dump(step.task_json, task_file)

    def _copy_core_tree(self, dest: pathlib.Path) -> None:
        core_module = importlib.import_module("hidori_core")
        core_package_path = pathlib.Path(core_module.__path__[0])
        ignores = shutil.ignore_patterns("*.pyc", "__pycache__")
        shutil.copytree(core_package_path, dest, ignore=ignores, dirs_exist_ok=True)


def create_driver(target_data: dict[str, Any]) -> Driver:
    driver_name = target_data.pop("driver", DEFAULT_DRIVER)
    return DRIVERS_REGISTRY[driver_name](target_data)

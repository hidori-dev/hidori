import dataclasses
import importlib
import json
import pathlib
import shutil
import tempfile
from typing import Any, Self

from hidori_common.typings import Pipeline, Transport
from hidori_core.schema.base import Schema

DEFAULT_DRIVER = "ssh"

DRIVERS_REGISTRY: dict[str, type["Driver"]] = {}


@dataclasses.dataclass
class PreparedPipeline:
    dirpath: tempfile.TemporaryDirectory[str]
    transport: Transport[Any]
    messages: list[dict[str, str]] = dataclasses.field(default_factory=list)


class Driver:
    schema: Schema
    # TODO: https://github.com/python/mypy/issues/11871
    transport_cls: type[Transport[Self]]  # type: ignore

    def __init_subclass__(cls, *, name: str) -> None:
        super().__init_subclass__()

        if name in DRIVERS_REGISTRY:
            raise RuntimeError(f"{name} driver is already registered.")
        # TODO: Verify that transport_cls matches the Transport protocol
        DRIVERS_REGISTRY[name] = cls

    def __init__(self, config: Any) -> None:
        self.schema.validate(config)

    @property
    def user(self) -> str:
        raise NotImplementedError()

    def prepare(self, pipeline: Pipeline) -> PreparedPipeline:
        dirpath = tempfile.TemporaryDirectory(prefix="hidori-")
        self.prepare_modules(dirpath.name)
        self.prepare_executor(dirpath.name)
        self.prepare_tasks(dirpath.name, pipeline)
        return PreparedPipeline(dirpath=dirpath, transport=self.transport_cls(self))

    def finalize(self, prepared_pipeline: PreparedPipeline) -> None:
        transport = prepared_pipeline.transport
        base_dir = prepared_pipeline.dirpath.name
        prepared_pipeline.messages.extend(transport.push(base_dir, base_dir))

    def invoke_executor(
        self, prepared_pipeline: PreparedPipeline, task_id: str
    ) -> None:
        transport = prepared_pipeline.transport
        base_dir = prepared_pipeline.dirpath.name
        executor_path = pathlib.Path(base_dir) / "executor.py"
        prepared_pipeline.messages.extend(
            transport.invoke(str(executor_path), [task_id])
        )

    def prepare_modules(self, temp_dir_path: str) -> None:
        # TODO: Driver should only pick required modules.
        # Use MODULES_REGISTRY and delivered modules for that
        # It will also allow third parties to define their own modules.
        # TODO: This (copying typing-extensions) is terrible.
        # Delete as soon as 3.7 drops.
        import typing_extensions

        ty_exts_path = typing_extensions.__file__
        tmp_ty_exts_path = pathlib.Path(temp_dir_path) / "typing_extensions.py"
        shutil.copyfile(ty_exts_path, tmp_ty_exts_path)
        tmp_core_path = pathlib.Path(temp_dir_path) / "hidori_core"
        self._copy_core_tree(tmp_core_path)

    def prepare_executor(self, temp_dir_path: str) -> None:
        # TODO: Use appropriate executor instead of a hardcoded remote
        runner_module = importlib.import_module("hidori_runner")
        executor_path = pathlib.Path(runner_module.__path__[0]) / "executors/remote.py"
        tmp_executor_path = pathlib.Path(temp_dir_path) / "executor.py"
        shutil.copyfile(executor_path, tmp_executor_path)

    def prepare_tasks(self, temp_dir_path: str, pipeline: Pipeline) -> None:
        for step in pipeline.steps:
            tmp_task_path = pathlib.Path(temp_dir_path) / f"task-{step.task_id}.json"
            with open(tmp_task_path, "w") as task_file:
                json.dump(step.task_json, task_file)

    def _copy_core_tree(self, dest: pathlib.Path) -> None:
        core_module = importlib.import_module("hidori_core")
        core_package_path = pathlib.Path(core_module.__path__[0])
        ignores = shutil.ignore_patterns("*.pyc", "__pycache__")
        shutil.copytree(core_package_path, dest, ignore=ignores, dirs_exist_ok=True)


def create_driver(target_data: dict[str, Any]) -> Driver:
    driver_name = target_data.pop("driver", DEFAULT_DRIVER)
    return DRIVERS_REGISTRY[driver_name](target_data)

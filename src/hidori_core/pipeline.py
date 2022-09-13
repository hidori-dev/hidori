import json
import pathlib
import shutil
import subprocess
import tempfile
from typing import Any

import tomllib

import hidori_core
import hidori_runner

SSH_OPTIONS = [
    "-o ControlMaster=auto",
    "-o ControlPath=~/.ssh/control-%r@%h:%p",
    "-o ControlPersist=yes",
]

PIPELINE_MODULES_REGISTRY: dict[str, type["PipelineStep"]] = {}

# TODO: Pipelines don't belong in hidori_core


class PipelineStep:
    def __init_subclass__(cls, /, module_name: str) -> None:
        super().__init_subclass__()

        if module_name in PIPELINE_MODULES_REGISTRY:
            raise RuntimeError(f"{module_name} module name is already registered.")
        PIPELINE_MODULES_REGISTRY[module_name] = cls

    def __init__(self, pipeline: "Pipeline") -> None:
        self._pipeline = pipeline

    def run(self) -> None:
        raise NotImplementedError()


class DefaultPipelineStep(PipelineStep, module_name="*"):
    def run(self):
        if self._pipeline.running:
            return

        self._pipeline.running = True
        self._pipeline.run_remote_modules()


class FilePushPipelineStep(PipelineStep, module_name="file-push"):
    def run(self):
        self._pipeline.running = True
        self._pipeline.run_remote_modules()


class Pipeline:
    @classmethod
    def from_toml_path(cls, path: str) -> "Pipeline":
        with open(path, "rb") as f:
            data = tomllib.load(f)

        return Pipeline(data)

    def __init__(self, data: dict[str, Any]) -> None:
        self.prepared = False
        self.running = False
        self._executor_dir = None
        self.steps: list[PipelineStep] = []

        self._data = data
        # TODO: Actually validate the provided data
        # TODO: Replace hardcoded vm host data
        # TODO: Add support for driver config val
        # TODO: Add support for remote_path config val
        # TODO: Extract driver-specific code to the drivers
        host_data = data["hosts"]["vm"]
        self.ssh_ip = host_data["ip"]
        self.ssh_user = host_data["user"]

        modules = [task["module"] for _, task in data["tasks"].items()]
        for module_name in modules:
            self.steps.append(
                PIPELINE_MODULES_REGISTRY.get(
                    module_name, PIPELINE_MODULES_REGISTRY["*"]
                )(self)
            )

    def prepare(self):
        # TODO: Remote runner should only take required modules.
        # Use MODULES_REGISTRY and self.modules for that
        # It will also allow third parties to define their own modules.
        # TODO: This should likely be part of the SSH driver
        with tempfile.TemporaryDirectory(prefix="hidori-") as tmpdirpath:
            # TODO: This is terrible. Delete as soon as 3.7 drops.
            import typing_extensions

            ty_exts_path = typing_extensions.__file__
            tmp_ty_exts_path = pathlib.Path(tmpdirpath) / "typing_extensions.py"
            shutil.copyfile(ty_exts_path, tmp_ty_exts_path)

            self._copy_core_tree("compat", tmpdirpath)
            self._copy_core_tree("modules", tmpdirpath)
            self._copy_core_tree("schema", tmpdirpath)
            self._copy_core_tree("utils", tmpdirpath)

            # TODO: Use appropriate executor instead of a hardcoded remote
            executor_path = (
                pathlib.Path(hidori_runner.__file__).parent / "executors/remote.py"
            )
            tmp_executor_path = pathlib.Path(tmpdirpath) / "executor.py"
            shutil.copyfile(executor_path, tmp_executor_path)

            tmp_tasks_path = pathlib.Path(tmpdirpath) / "tasks.json"
            with open(tmp_tasks_path, "w") as tasks_file:
                json.dump(self._data["tasks"], tasks_file)

            # TO THE STARS!
            # TODO: Part of the transport
            scp_cmd = (
                f"scp {' '.join(SSH_OPTIONS)} -qr {tmpdirpath} "
                f"{self.ssh_user}@{self.ssh_ip}:{tmpdirpath}"
            )
            subprocess.run(scp_cmd.split())

        self._executor_dir = tmpdirpath
        self._prepared = True

    def _copy_core_tree(self, dirname: str, dest: str) -> None:
        tmp_core_init_path = pathlib.Path(hidori_core.__file__).parent / "__init__.py"
        open(tmp_core_init_path, "w").close()
        core_package_path = pathlib.Path(hidori_core.__file__).parent / dirname
        tmp_core_package_path = pathlib.Path(dest) / f"hidori_core/{dirname}"
        shutil.copytree(
            str(core_package_path), str(tmp_core_package_path), dirs_exist_ok=True
        )

    def run(self):
        if not self._prepared:
            raise RuntimeError("pipeline is not prepared")

        for pipeline_step in self.steps:
            pipeline_step.run()

    def run_remote_modules(self):
        # TODO: Rename this method - modules won't always run on remote.
        # TODO: Impl a dedicated ssh Transport class
        # TODO: Replace subprocess calls
        runner_ssh_cmd = (
            f"ssh {' '.join(SSH_OPTIONS)} -qt {self.ssh_user}@{self.ssh_ip} "
            f"python3 {self._executor_dir}/executor.py"
        )
        subprocess.run(runner_ssh_cmd.split())

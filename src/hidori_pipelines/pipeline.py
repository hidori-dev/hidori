import json
import pathlib
import shutil
import subprocess
import tempfile
import uuid
from typing import Any

import hidori_core
import hidori_runner
from hidori_common import CLIMessageWriter
from hidori_core.modules import MODULES_REGISTRY

SSH_OPTIONS = [
    "-o ControlMaster=auto",
    "-o ControlPath=~/.ssh/control-%r@%h:%p",
    "-o ControlPersist=yes",
]

PIPELINE_MODULES_REGISTRY: dict[str, type["PipelineStep"]] = {}


class PipelineStep:
    def __init_subclass__(cls, *, module_name: str) -> None:
        super().__init_subclass__()

        if module_name not in MODULES_REGISTRY and module_name != "*":
            raise RuntimeError(f"{module_name} module does not exist.")

        if module_name in PIPELINE_MODULES_REGISTRY:
            raise RuntimeError(f"{module_name} module name is already registered.")
        PIPELINE_MODULES_REGISTRY[module_name] = cls

    def __init__(self, task_name: str, task_data: dict[str, Any]) -> None:
        self._task_name = task_name
        self._task_id = uuid.uuid4().hex
        self._task_data = task_data

        module_name = task_data["module"]
        if module_name not in MODULES_REGISTRY:
            raise RuntimeError(f"{module_name} module does not exist.")

    @property
    def task_id(self):
        return self._task_id

    @property
    def task_json(self):
        return {"name": self._task_name, "data": self._task_data}

    def run(self, pipeline: "Pipeline") -> None:
        raise NotImplementedError()


class DefaultPipelineStep(PipelineStep, module_name="*"):
    def run(self, pipeline: "Pipeline") -> None:
        pipeline.run_remote_module(self.task_id)


# class FilePushPipelineStep(PipelineStep, module_name="file-push"):
#     def run(self, pipeline: "Pipeline") -> None:
#         pipeline.run_remote_module(self.task_id)


class Pipeline:
    def __init__(self, host_data: dict[str, Any], tasks_data: dict[str, Any]) -> None:
        self.prepared = False
        self._executor_dir = None

        self._steps: list[PipelineStep] = self._create_steps(tasks_data)
        # TODO: Add support for driver config val
        # TODO: Add support for remote_path config val
        # TODO: Extract driver-specific code to the drivers
        self.target = host_data["target"]
        self.ssh_ip = host_data["data"]["ip"]
        self.ssh_user = host_data["data"]["user"]
        self._message_writer = CLIMessageWriter(user=self.ssh_user, target=self.target)

    def _create_steps(self, tasks_data: dict[str, Any]) -> list[PipelineStep]:
        steps: list[PipelineStep] = []
        for name, data in tasks_data.items():
            module_name = data["module"]
            steps.append(
                PIPELINE_MODULES_REGISTRY.get(
                    module_name, PIPELINE_MODULES_REGISTRY["*"]
                )(name, data)
            )
        return steps

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

            for step in self._steps:
                tmp_task_path = pathlib.Path(tmpdirpath) / f"task-{step.task_id}.json"
                with open(tmp_task_path, "w") as task_file:
                    json.dump(step.task_json, task_file)

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

        for pipeline_step in self._steps:
            pipeline_step.run(self)

        self._message_writer.print_summary()

    def run_remote_module(self, task_id: str) -> None:
        # TODO: Rename this method - modules won't always run on remote.
        # TODO: Impl a dedicated ssh Transport class
        # TODO: Replace subprocess calls
        runner_ssh_cmd = (
            f"ssh {' '.join(SSH_OPTIONS)} -qt {self.ssh_user}@{self.ssh_ip} "
            f"python3 {self._executor_dir}/executor.py {task_id}"
        )
        results = subprocess.run(runner_ssh_cmd.split(), capture_output=True, text=True)
        messages_data: list[dict[str, Any]] = []
        for message in results.stdout.splitlines():
            try:
                messages_data.append(json.loads(message))
            except json.JSONDecodeError:
                # TODO: For now let's just ignore stdout that is not JSON
                continue
        self._message_writer.print_all(messages_data)

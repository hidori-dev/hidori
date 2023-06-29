import uuid
from typing import Any, TypedDict

from hidori_common import ConsolePrinter
from hidori_core.modules import MODULES_REGISTRY
from hidori_runner.drivers.base import Driver, PreparedExchange

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
    def task_id(self) -> str:
        return self._task_id

    @property
    def task_json(self) -> dict[str, Any]:
        return {"name": self._task_name, "data": self._task_data}


class DefaultPipelineStep(PipelineStep, module_name="*"):
    ...


class DestinationData(TypedDict):
    target: str
    driver: Driver


class Pipeline:
    def __init__(
        self, destination_data: DestinationData, tasks_data: dict[str, Any]
    ) -> None:
        self._steps: list[PipelineStep] = self._create_steps(tasks_data)
        self._exchange: PreparedExchange | None = None
        self.target = destination_data["target"]
        self.driver = destination_data["driver"]
        self._printer = ConsolePrinter(user=self.driver.user, target=self.target)

    @property
    def steps(self) -> list[PipelineStep]:
        return self._steps

    @property
    def has_completed(self) -> bool:
        return not self._steps

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

    def prepare(self) -> None:
        self._exchange = self.driver.prepare_pipeline(self)

    async def finalize(self) -> None:
        if not self._exchange:
            raise RuntimeError("pipeline is not prepared")

        await self.driver.finalize(self._exchange)
        self.handle_messages()

    async def invoke_step(self) -> None:
        if not self._exchange:
            raise RuntimeError("pipeline is not prepared")

        step = self._steps.pop(0)
        await self.driver.invoke_executor(self._exchange, step.task_id)
        self.handle_messages()

    def handle_messages(self) -> None:
        if not self._exchange:
            raise RuntimeError("pipeline is not prepared")

        if self._exchange.messages:
            self._printer.print_all(self._exchange.messages)
            self._exchange.messages.clear()

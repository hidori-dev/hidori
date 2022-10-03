from typing import Any, Iterable, Protocol


class PipelineStep(Protocol):
    @property
    def task_id(self) -> str:
        ...

    @property
    def task_json(self) -> dict[str, Any]:
        ...


class Pipeline(Protocol):
    @property
    def steps(self) -> Iterable[PipelineStep]:
        ...

    def prepare(self) -> None:
        ...

    def run(self) -> None:
        ...

    def invoke_task(self, task_id: str) -> None:
        ...

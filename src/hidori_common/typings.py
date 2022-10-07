from typing import Any, Iterable, Protocol, TypeVar

DT = TypeVar("DT", bound="Driver")


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


class Driver(Protocol):
    ...


class Transport(Protocol[DT]):
    _driver: DT

    def __init__(self, driver: DT) -> None:
        self._driver = driver

    def push(self, source: str, dest: str) -> None:
        ...

    def invoke(self, path: str, args: list[str]) -> str:
        ...

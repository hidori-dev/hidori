import pathlib
from typing import Any, ClassVar, Iterable, Protocol, TypeVar

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


class Driver(Protocol):
    ...


class Transport(Protocol[DT]):
    # TODO: Add pre-flight env detection and verification
    _driver: DT
    name: ClassVar[str]

    def __init_subclass__(cls, name: str) -> None:
        cls.name = name

    def __init__(self, driver: DT) -> None:
        self._driver = driver

    def push(self, exchange_id: str, source: pathlib.Path) -> list[dict[str, str]]:
        ...

    def invoke(
        self, exchange_id: str, path: str, args: list[str]
    ) -> list[dict[str, str]]:
        ...

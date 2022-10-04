from typing import Protocol, TypeVar


class Driver(Protocol):
    ...


T = TypeVar("T", bound=Driver)


class Transport(Protocol[T]):
    _driver: T

    def __init__(self, driver: T) -> None:
        self._driver = driver

    def push(self, source: str, dest: str) -> None:
        ...

    def invoke(self, path: str, args: list[str]) -> str:
        ...

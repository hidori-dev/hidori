from typing import Generic, TypeVar

from hidori_runner import drivers

T = TypeVar("T", bound="drivers.Driver")


class Transport(Generic[T]):
    def __init__(self, driver: T) -> None:
        self._driver = driver

    def push(self, source: str, dest: str) -> None:
        ...

    def invoke(self, path: str) -> None:
        ...

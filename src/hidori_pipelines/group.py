from typing import Any, Iterable, Iterator

# TODO: Remove this type ignore when pre-commit.ci is updated to py3.11
import tomllib  # type: ignore

from hidori_core.schema import Schema
from hidori_pipelines.pipeline import Pipeline
from hidori_runner.drivers import create_driver


class PipelineSchema(Schema):
    hosts: dict[str, dict[str, Any]]
    tasks: dict[str, dict[str, Any]]


class PipelineGroup(Iterable[Pipeline]):
    @classmethod
    def from_toml_path(cls, path: str) -> "PipelineGroup":
        with open(path, "rb") as f:
            return cls(tomllib.load(f))

    def __init__(self, data: dict[str, Any]) -> None:
        schema = PipelineSchema()
        schema.validate(data)

        self._hosts_data = [
            {"target": host, "driver": create_driver(host_data)}
            for host, host_data in data["hosts"].items()
        ]
        self._pipeline_data = data["tasks"]
        self._hosts = data["hosts"].keys()
        self._current = 0

    def __iter__(self) -> Iterator[Pipeline]:
        return self

    def __next__(self) -> Pipeline:
        if self._current >= len(self._hosts_data):
            raise StopIteration()

        host_data = self._hosts_data[self._current]
        self._current += 1
        return Pipeline(host_data, self._pipeline_data)

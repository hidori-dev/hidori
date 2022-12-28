import tomllib
from typing import Any, Iterable, Iterator

from hidori_core.schema import Schema
from hidori_pipelines.pipeline import Pipeline, TargetData
from hidori_runner.drivers import create_driver


class PipelineSchema(Schema):
    targets: dict[str, dict[str, Any]]
    tasks: dict[str, dict[str, Any]]


class PipelineGroup(Iterable[Pipeline]):
    @classmethod
    def from_toml_path(cls, path: str) -> "PipelineGroup":
        with open(path, "rb") as f:
            return cls(tomllib.load(f))

    def __init__(self, data: dict[str, Any]) -> None:
        schema = PipelineSchema()
        schema.validate(data)

        self._targets_data: list[TargetData] = [
            {"target": target, "driver": create_driver(target_data)}
            for target, target_data in data["targets"].items()
        ]
        self._pipeline_data = data["tasks"]
        self._targets = data["targets"].keys()
        self._current = 0

    def __iter__(self) -> Iterator[Pipeline]:
        return self

    def __next__(self) -> Pipeline:
        if self._current >= len(self._targets_data):
            raise StopIteration()

        target_data = self._targets_data[self._current]
        self._current += 1
        return Pipeline(target_data, self._pipeline_data)

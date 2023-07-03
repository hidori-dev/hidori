import asyncio
import tomllib
from typing import Any, Iterable, Iterator, Literal

from hidori_core.schema import Schema
from hidori_pipelines.pipeline import DestinationData, Pipeline
from hidori_runner.drivers import create_driver


class PipelineConfig(Schema):
    on_fail: Literal["abort-failed", "abort-all", "continue"]


class PipelineSchema(Schema):
    config: PipelineConfig | None
    destinations: dict[str, dict[str, Any]]
    tasks: dict[str, dict[str, Any]]


class PipelineGroup(Iterable[Pipeline]):
    @classmethod
    def from_toml_path(cls, path: str) -> "PipelineGroup":
        with open(path, "rb") as f:
            return cls(tomllib.load(f))

    def __init__(self, data: dict[str, Any]) -> None:
        schema = PipelineSchema()
        schema.validate(data)

        self._config = data.get("config", {"on_fail": "abort-failed"})
        self._destinations_data: list[DestinationData] = [
            {"target": target, "driver": create_driver(destination_data)}
            for target, destination_data in data["destinations"].items()
        ]
        self._pipeline_data = data["tasks"]
        self._current = 0

    def __iter__(self) -> Iterator[Pipeline]:
        return self

    def __next__(self) -> Pipeline:
        if self._current >= len(self._destinations_data):
            raise StopIteration()

        destination_data = self._destinations_data[self._current]
        self._current += 1
        return Pipeline(destination_data, self._pipeline_data)

    async def run(self) -> None:
        pipelines = list(self.prepare_pipelines())
        async with asyncio.TaskGroup() as tg:
            for pipeline in pipelines:
                tg.create_task(pipeline.finalize())

        pipelines = self._filter_out_failed_pipelines(pipelines, critical_task=True)
        while not all([p.has_completed for p in pipelines]):
            async with asyncio.TaskGroup() as tg:
                for pipeline in pipelines:
                    tg.create_task(pipeline.invoke_step())
            pipelines = self._filter_out_failed_pipelines(pipelines)

    def prepare_pipelines(self) -> Iterator[Pipeline]:
        for pipeline in self:
            pipeline.prepare()
            yield pipeline

    def _filter_out_failed_pipelines(
        self, pipelines: list[Pipeline], critical_task: bool = False
    ) -> list[Pipeline]:
        has_any_failed = any([p.has_failed for p in pipelines])
        if has_any_failed and self._config["on_fail"] == "abort-all":
            return []
        elif has_any_failed and self._config["on_fail"] == "abort-failed":
            return [p for p in pipelines if not p.has_failed]
        elif has_any_failed and critical_task:
            return [p for p in pipelines if not p.has_failed]
        elif self._config["on_fail"] == "continue":
            return pipelines
        else:
            return pipelines

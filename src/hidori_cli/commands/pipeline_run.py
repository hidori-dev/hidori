import pathlib
from dataclasses import dataclass, field

from hidori_cli.commands.base import BaseData, Command
from hidori_pipelines import PipelineGroup


@dataclass
class PipelineRunData(BaseData):
    pipeline_path: pathlib.Path = field(
        metadata={"help": "Path to the TOML pipeline file"}
    )


class PipelineRunCommand(Command[PipelineRunData]):
    """pipeline-run command"""

    data_cls = PipelineRunData

    def execute(self, data: PipelineRunData) -> None:
        group = PipelineGroup.from_toml_path(str(data.pipeline_path))
        for pipeline in group:
            pipeline.prepare()
            pipeline.run()

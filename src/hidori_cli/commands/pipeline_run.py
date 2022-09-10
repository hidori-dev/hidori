from dataclasses import dataclass, field

from hidori_cli.commands.base import BaseData, Command
from hidori_core.pipeline import Pipeline


@dataclass
class PipelineRunData(BaseData):
    # TODO: Filepath type with validation that file exists?
    pipeline_file: str = field(metadata={"help": "Path to the TOML pipeline file"})


class PipelineRunCommand(Command[PipelineRunData]):
    """pipeline-run command"""

    data_cls = PipelineRunData

    def execute(self, data: PipelineRunData) -> None:
        pipeline = Pipeline.from_toml_path(data.pipeline_file)
        pipeline.prepare()
        pipeline.run()

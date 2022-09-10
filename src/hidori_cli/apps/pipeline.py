from hidori_cli.apps.base import BaseCLIApplication


class HidoriPipelineApplication(BaseCLIApplication):
    """hidori-pipeline CLI."""


def main() -> None:
    app = HidoriPipelineApplication()
    app.run()

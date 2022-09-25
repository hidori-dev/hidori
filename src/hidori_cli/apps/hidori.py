from hidori_cli.apps.base import BaseCLIApplication


class HidoriHidoriApplication(BaseCLIApplication):
    """hidori CLI."""


def main() -> None:
    app = HidoriHidoriApplication()
    app.run()

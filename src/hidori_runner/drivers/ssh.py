from typing import Optional

from hidori_core.schema import Schema
from hidori_runner import transports
from hidori_runner.drivers.base import Driver


class SSHSchema(Schema):
    # TODO: Add support for remote_path config val
    target: str
    user: str
    port: Optional[str]


class SSHDriver(Driver, name="ssh"):
    schema = SSHSchema()
    transport_cls = transports.SSHTransport

    def init(self, config: dict[str, str]) -> None:
        self.ssh_target = config["target"]
        self.ssh_user = config["user"]
        self.ssh_port = config.get("port", "22")

    @property
    def user(self) -> str:
        return self.ssh_user

    @property
    def target(self) -> str:
        return self.ssh_target

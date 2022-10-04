from hidori_core.schema import Schema
from hidori_runner import transports
from hidori_runner.drivers.base import Driver


class SSHSchema(Schema):
    # TODO: Add support for remote_path config val
    ip: str
    user: str


class SSHDriver(Driver, name="ssh"):
    schema = SSHSchema()
    transport_cls = transports.SSHTransport

    def __init__(self, config: dict[str, str]) -> None:
        super().__init__(config)
        self.ssh_ip = config["ip"]
        self.ssh_user = config["user"]

    @property
    def user(self) -> str:
        return self.ssh_user

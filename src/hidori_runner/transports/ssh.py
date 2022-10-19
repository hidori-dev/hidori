import subprocess
from typing import TYPE_CHECKING

from hidori_common.typings import Transport
from hidori_runner.transports.utils import get_messages

if TYPE_CHECKING:
    # TODO: Seems to be https://github.com/PyCQA/pyflakes/issues/567
    from hidori_runner.drivers import SSHDriver  # noqa: F401

SSH_OPTIONS = " ".join(
    [
        "-o ControlMaster=auto",
        "-o ControlPath=~/.ssh/control-%r@%h:%p",
        "-o ControlPersist=yes",
    ]
)


def run_command(popen_cmd: list[str]) -> str:
    results = subprocess.run(popen_cmd, capture_output=True, text=True)
    if results.returncode == 0:
        output = results.stdout
    else:
        output = results.stderr if results.stderr else results.stdout

    return output.strip()


class SSHTransport(Transport["SSHDriver"], name="ssh"):
    def push(self, source: str, dest: str) -> list[dict[str, str]]:
        ssh_user = self._driver.ssh_user
        ssh_ip = self._driver.ssh_ip
        ssh_port = self._driver.ssh_port

        cmd = (
            f"scp {SSH_OPTIONS} -qr -P {ssh_port} {source} "
            f"{ssh_user}@{ssh_ip}:{dest}".split()
        )
        # TO THE STARS!
        return get_messages(run_command(cmd), self.name)

    def invoke(self, path: str, args: list[str]) -> list[dict[str, str]]:
        ssh_user = self._driver.ssh_user
        ssh_ip = self._driver.ssh_ip
        ssh_port = self._driver.ssh_port

        cmd = (
            f"ssh {SSH_OPTIONS} -qt -p {ssh_port} "
            f"{ssh_user}@{ssh_ip} python3 {path}".split()
        )
        cmd.extend(args)
        return get_messages(run_command(cmd), self.name)

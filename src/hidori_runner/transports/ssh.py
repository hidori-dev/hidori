import pathlib
import subprocess
from typing import TYPE_CHECKING

from hidori_common.dirs import get_tmp_home
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


def run_command(popen_cmd: list[str]) -> tuple[bool, str]:
    results = subprocess.run(popen_cmd, capture_output=True, text=True)
    if results.returncode == 0:
        output = results.stdout
    else:
        output = results.stderr if results.stderr else results.stdout

    return results.returncode == 0, output.strip()


def get_exchange_dir_path(exchange_id: str) -> pathlib.Path:
    return get_tmp_home() / f"hidori-exchange-{exchange_id}"


class SSHTransport(Transport["SSHDriver"], name="ssh"):
    def push(self, exchange_id: str, source: pathlib.Path) -> list[dict[str, str]]:
        ssh_user = self._driver.ssh_user
        ssh_target = self._driver.ssh_target
        ssh_port = self._driver.ssh_port
        exchange_path = get_exchange_dir_path(exchange_id)

        cmd = (
            f"scp {SSH_OPTIONS} -prq -P {ssh_port} {source} "
            f"{ssh_user}@{ssh_target}:{exchange_path}"
        ).split()
        # TO THE STARS!
        success, output = run_command(cmd)
        return get_messages(output, self.name, ignore_parse_error=success)

    def invoke(
        self, exchange_id: str, path: str, args: list[str]
    ) -> list[dict[str, str]]:
        ssh_user = self._driver.ssh_user
        ssh_target = self._driver.ssh_target
        ssh_port = self._driver.ssh_port
        invoked_path = get_exchange_dir_path(exchange_id) / path

        cmd = (
            f"ssh {SSH_OPTIONS} -qT -p {ssh_port} "
            f"{ssh_user}@{ssh_target} python3 {invoked_path}"
        ).split()
        cmd.extend(args)
        success, output = run_command(cmd)
        return get_messages(output, self.name, ignore_parse_error=success)

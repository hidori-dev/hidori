import asyncio
import pathlib
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


async def run_command(popen_cmd: str) -> tuple[bool, str]:
    proc = await asyncio.create_subprocess_shell(
        popen_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    stdout, stderr = stdout.strip(), stderr.strip()
    if proc.returncode == 0:
        output = stdout
    else:
        output = stderr if stderr else stdout

    output = (output or b"").decode()
    return proc.returncode == 0, output


def get_exchange_dir_path(exchange_id: str) -> pathlib.Path:
    return get_tmp_home() / f"hidori-exchange-{exchange_id}"


class SSHTransport(Transport["SSHDriver"], name="ssh"):
    async def push(
        self, exchange_id: str, source: pathlib.Path
    ) -> list[dict[str, str]]:
        ssh_user = self._driver.ssh_user
        ssh_target = self._driver.ssh_target
        ssh_port = self._driver.ssh_port
        exchange_path = get_exchange_dir_path(exchange_id)

        cmd = (
            f"scp {SSH_OPTIONS} -prq -P {ssh_port} {source} "
            f"{ssh_user}@{ssh_target}:{exchange_path}"
        )
        # TO THE STARS!
        success, output = await run_command(cmd)
        return get_messages(output, self.name, ignore_parse_error=success)

    async def invoke(
        self, exchange_id: str, path: str, args: str
    ) -> list[dict[str, str]]:
        ssh_user = self._driver.ssh_user
        ssh_target = self._driver.ssh_target
        ssh_port = self._driver.ssh_port
        invoked_path = get_exchange_dir_path(exchange_id) / path

        cmd = (
            f"ssh {SSH_OPTIONS} -qT -p {ssh_port} "
            f"{ssh_user}@{ssh_target} python3 {invoked_path} "
            f"{args}"
        )
        success, output = await run_command(cmd)
        return get_messages(output, self.name, ignore_parse_error=success)

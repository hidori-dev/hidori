from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING

from hidori_common.typings import Transport
from hidori_runner.transports.errors import TransportError

if TYPE_CHECKING:
    from hidori_runner.drivers import SSHDriver

SSH_OPTIONS = " ".join(
    [
        "-o ControlMaster=auto",
        "-o ControlPath=~/.ssh/control-%r@%h:%p",
        "-o ControlPersist=yes",
    ]
)


def run_command(popen_cmd: list[str]) -> str:
    results = subprocess.run(popen_cmd, capture_output=True, text=True)
    if results.returncode != 0:
        raise TransportError(
            json.dumps(
                {
                    "type": "error",
                    "task": "INTERNAL-SSH-TRANSPORT",
                    "message": results.stderr.strip(),
                }
            )
        )

    return results.stdout


class SSHTransport(Transport[SSHDriver]):
    def push(self, source: str, dest: str) -> None:
        ssh_user = self._driver.ssh_user
        ssh_ip = self._driver.ssh_ip
        ssh_port = self._driver.ssh_port

        cmd = (
            f"scp {SSH_OPTIONS} -qr -P {ssh_port} {source} "
            f"{ssh_user}@{ssh_ip}:{dest}".split()
        )
        # TO THE STARS!
        run_command(cmd)

    def invoke(self, path: str, args: list[str]) -> str:
        ssh_user = self._driver.ssh_user
        ssh_ip = self._driver.ssh_ip
        ssh_port = self._driver.ssh_port

        cmd = (
            f"ssh {SSH_OPTIONS} -qt -p {ssh_port} "
            f"{ssh_user}@{ssh_ip} python3 {path}".split()
        )
        cmd.extend(args)
        return run_command(cmd)

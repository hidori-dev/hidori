from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

from hidori_common.typings import Transport

if TYPE_CHECKING:
    from hidori_runner.drivers import SSHDriver

SSH_OPTIONS = " ".join(
    [
        "-o ControlMaster=auto",
        "-o ControlPath=~/.ssh/control-%r@%h:%p",
        "-o ControlPersist=yes",
    ]
)


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
        subprocess.run(cmd)

    def invoke(self, path: str, args: list[str]) -> str:
        ssh_user = self._driver.ssh_user
        ssh_ip = self._driver.ssh_ip
        ssh_port = self._driver.ssh_port

        cmd = (
            f"ssh {SSH_OPTIONS} -qt -p {ssh_port} "
            f"{ssh_user}@{ssh_ip} python3 {path}".split()
        )
        cmd.extend(args)
        results = subprocess.run(cmd, capture_output=True, text=True)
        # TODO: raise an exception if something wrong happened
        return results.stdout

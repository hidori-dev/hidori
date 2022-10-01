import subprocess

# TODO: Seems to be https://github.com/PyCQA/pyflakes/issues/567
from hidori_runner import drivers  # noqa: F401
from hidori_runner.transports.base import Transport

SSH_OPTIONS = " ".join(
    [
        "-o ControlMaster=auto",
        "-o ControlPath=~/.ssh/control-%r@%h:%p",
        "-o ControlPersist=yes",
    ]
)


class SSHTransport(Transport["drivers.SSHDriver"]):
    def push(self, source: str, dest: str) -> None:
        ssh_user = self._driver.ssh_user
        ssh_ip = self._driver.ip

        scp_cmd = f"scp {SSH_OPTIONS} -qr {source} {ssh_user}@{ssh_ip}:{dest}"
        # TO THE STARS!
        subprocess.run(scp_cmd.split())

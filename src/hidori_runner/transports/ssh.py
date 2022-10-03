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

        cmd = f"scp {SSH_OPTIONS} -qr {source} {ssh_user}@{ssh_ip}:{dest}".split()
        # TO THE STARS!
        subprocess.run(cmd)

    def invok(self, path: str, args: list[str]) -> str:
        ssh_user = self._driver.ssh_user
        ssh_ip = self._driver.ip

        cmd = f"ssh {SSH_OPTIONS} -qt {ssh_user}@{ssh_ip} python3 {path}".split()
        cmd.extend(args)
        results = subprocess.run(cmd, capture_output=True, text=True)
        return results.stdout

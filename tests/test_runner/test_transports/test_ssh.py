from __future__ import annotations

import json
import subprocess
from unittest.mock import Mock, patch

import pytest

from hidori_runner.transports.errors import TransportError
from hidori_runner.transports.ssh import SSHTransport


def subproc_scp_ok(*popenargs: str, capture_output: bool, text: bool):
    return subprocess.CompletedProcess[str](
        args=popenargs,
        returncode=0,
        stdout="",
        stderr="",
    )


def subproc_scp_con_closed(*popenargs: str, capture_output: bool, text: bool):
    return subprocess.CompletedProcess[str](
        args=popenargs,
        returncode=255,
        stdout="",
        stderr="scp: Connection closed\n",
    )


def subproc_scp_error(*popenargs: str, capture_output: bool, text: bool):
    return subprocess.CompletedProcess[str](
        args=popenargs,
        returncode=1,
        stdout="",
        stderr="scp: Some generic error\n",
    )


@pytest.fixture(scope="module")
def ssh_transport():
    driver = Mock(ssh_user="user", ssh_ip="127.0.0.1", ssh_port="50022")
    return SSHTransport(driver)


def test_transport_push_ok(ssh_transport: SSHTransport):
    with patch("subprocess.run", side_effect=subproc_scp_ok) as subprocess_run:
        ssh_transport.push("/foo/bar", "/bar/foo")

    assert subprocess_run.call_count == 1
    assert subprocess_run.call_args.args == (
        [
            "scp",
            "-o",
            "ControlMaster=auto",
            "-o",
            "ControlPath=~/.ssh/control-%r@%h:%p",
            "-o",
            "ControlPersist=yes",
            "-qr",
            "-P",
            "50022",
            "/foo/bar",
            "user@127.0.0.1:/bar/foo",
        ],
    )
    assert subprocess_run.call_args.kwargs == {"capture_output": True, "text": True}


def test_transport_push_con_error(ssh_transport: SSHTransport):
    with patch("subprocess.run", side_effect=subproc_scp_con_closed) as subprocess_run:
        with pytest.raises(TransportError) as e:
            ssh_transport.push("/foo/bar", "/bar/foo")

    assert json.loads(str(e.value)) == {
        "type": "error",
        "task": "INTERNAL-SSH-TRANSPORT",
        "message": "scp: Connection closed",
    }
    assert subprocess_run.call_count == 1


def test_transport_push_generic_error(ssh_transport: SSHTransport):
    with patch("subprocess.run", side_effect=subproc_scp_error) as subprocess_run:
        with pytest.raises(TransportError) as e:
            ssh_transport.push("/foo/bar", "/bar/foo")

    assert json.loads(str(e.value)) == {
        "type": "error",
        "task": "INTERNAL-SSH-TRANSPORT",
        "message": "scp: Some generic error",
    }
    assert subprocess_run.call_count == 1

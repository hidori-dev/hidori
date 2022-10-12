import json
import subprocess
from unittest.mock import Mock, patch

import pytest

from hidori_runner.transports.errors import TransportError
from hidori_runner.transports.ssh import SSHTransport

SUCCESS_EXEC_MSG = json.dumps(
    {"type": "success", "task": "Test task", "message": "test task succeeded"}
)
FAILED_EXEC_MSG = json.dumps(
    {"type": "error", "task": "Test task", "message": "Traceback ..."}
)


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


def subproc_exec_ok(*popenargs: str, capture_output: bool, text: bool):
    return subprocess.CompletedProcess[str](
        args=popenargs,
        returncode=0,
        stdout=f"{SUCCESS_EXEC_MSG}\n",
        stderr="",
    )


def subproc_no_exec(*popenargs: str, capture_output: bool, text: bool):
    return subprocess.CompletedProcess[str](
        args=popenargs,
        returncode=2,
        stdout="python3: can't open file '/foo'\n",
        stderr="",
    )


def subproc_exec_failed(*popenargs: str, capture_output: bool, text: bool):
    return subprocess.CompletedProcess[str](
        args=popenargs,
        returncode=0,
        stdout=f"{FAILED_EXEC_MSG}\n",
        stderr="",
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


def test_transport_invoke_executor_ok(ssh_transport: SSHTransport):
    with patch("subprocess.run", side_effect=subproc_exec_ok) as subprocess_run:
        result = ssh_transport.invoke("/hidori/executor.py", ["TASK-ID"])

    assert result == SUCCESS_EXEC_MSG

    assert subprocess_run.call_count == 1
    assert subprocess_run.call_args.args == (
        [
            "ssh",
            "-o",
            "ControlMaster=auto",
            "-o",
            "ControlPath=~/.ssh/control-%r@%h:%p",
            "-o",
            "ControlPersist=yes",
            "-qt",
            "-p",
            "50022",
            "user@127.0.0.1",
            "python3",
            "/hidori/executor.py",
            "TASK-ID",
        ],
    )
    assert subprocess_run.call_args.kwargs == {"capture_output": True, "text": True}


def test_transport_invoke_no_executor_error(ssh_transport: SSHTransport):
    with patch("subprocess.run", side_effect=subproc_no_exec) as subprocess_run:
        with pytest.raises(TransportError) as e:
            ssh_transport.invoke("/foo", [])

    assert json.loads(str(e.value)) == {
        "type": "error",
        "task": "INTERNAL-SSH-TRANSPORT",
        "message": "python3: can't open file '/foo'",
    }
    assert subprocess_run.call_count == 1


def test_transport_invoke_executor_failed_error(ssh_transport: SSHTransport):
    with patch("subprocess.run", side_effect=subproc_exec_failed) as subprocess_run:
        result = ssh_transport.invoke("/hidori/executor.py", ["TASK-ID"])

    assert result == FAILED_EXEC_MSG

    assert subprocess_run.call_count == 1

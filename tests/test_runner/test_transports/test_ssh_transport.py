import json
import pathlib
from unittest.mock import AsyncMock, Mock, patch

import pytest

from hidori_runner.transports.ssh import SSHTransport

SUCCESS_EXEC_MSG = json.dumps(
    {"type": "success", "task": "Test task", "message": "test task succeeded"}
).encode()
FAILED_EXEC_MSG = json.dumps(
    {"type": "error", "task": "Test task", "message": "Traceback ..."}
).encode()
FAILED_SYSTEM_MSG = json.dumps(
    {"type": "error", "task": "system", "message": "internal error"}
).encode()


def subproc_coro_patch(retcode: int, stdout: bytes = b"", stderr: bytes = b""):
    stdout = stdout + b"\n"
    stderr = stderr + b"\n"
    return patch(
        "asyncio.create_subprocess_shell",
        AsyncMock(
            return_value=Mock(
                returncode=retcode, communicate=AsyncMock(return_value=(stdout, stderr))
            )
        ),
    )


@pytest.fixture(scope="module")
def ssh_transport():
    driver = Mock(ssh_user="user", ssh_target="127.0.0.1", ssh_port="50022")
    return SSHTransport(driver)


@pytest.mark.asyncio
async def test_transport_push_ok(ssh_transport: SSHTransport):
    with subproc_coro_patch(retcode=0) as proc:
        messages = await ssh_transport.push("42", pathlib.Path("/foo/bar"))

    assert messages == []
    assert proc.call_count == 1
    assert proc.call_args.args == (
        "scp -o ControlMaster=auto -o ControlPath=~/.ssh/control-%r@%h:%p "
        "-o ControlPersist=yes -prq -P 50022 /foo/bar "
        "user@127.0.0.1:/tmp/hidori-exchange-42",
    )
    assert proc.call_args.kwargs == {"stdout": -1, "stderr": -1}


@pytest.mark.asyncio
async def test_transport_push_con_error(ssh_transport: SSHTransport):
    with subproc_coro_patch(retcode=255, stderr=b"scp: Connection closed") as proc:
        messages = await ssh_transport.push("42", pathlib.Path("/foo/bar"))

    assert messages == [
        {
            "type": "error",
            "task": "INTERNAL-SSH-TRANSPORT",
            "message": "scp: Connection closed",
        }
    ]
    assert proc.call_count == 1


@pytest.mark.asyncio
async def test_transport_push_generic_error(ssh_transport: SSHTransport):
    with subproc_coro_patch(retcode=1, stderr=b"scp: Some generic error") as proc:
        messages = await ssh_transport.push("42", pathlib.Path("/foo/bar"))

    assert messages == [
        {
            "type": "error",
            "task": "INTERNAL-SSH-TRANSPORT",
            "message": "scp: Some generic error",
        }
    ]
    assert proc.call_count == 1


@pytest.mark.asyncio
async def test_transport_invoke_executor_ok(ssh_transport: SSHTransport):
    with subproc_coro_patch(retcode=0, stdout=SUCCESS_EXEC_MSG) as proc:
        messages = await ssh_transport.invoke("42", "executor.py", "TASK-ID")

    assert messages == [json.loads(SUCCESS_EXEC_MSG)]
    assert proc.call_count == 1
    assert proc.call_args.args == (
        "ssh -o ControlMaster=auto -o ControlPath=~/.ssh/control-%r@%h:%p "
        "-o ControlPersist=yes -qT -p 50022 user@127.0.0.1 "
        "python3 /tmp/hidori-exchange-42/executor.py TASK-ID",
    )
    assert proc.call_args.kwargs == {"stdout": -1, "stderr": -1}


@pytest.mark.asyncio
async def test_transport_invoke_no_executor_error(ssh_transport: SSHTransport):
    expected_stdout = b"python3: can't open file '/foo'"
    with subproc_coro_patch(retcode=2, stdout=expected_stdout) as proc:
        messages = await ssh_transport.invoke("42", "/foo", "")

    assert messages == [
        {
            "type": "error",
            "task": "INTERNAL-SSH-TRANSPORT",
            "message": "python3: can't open file '/foo'",
        }
    ]
    assert proc.call_count == 1


@pytest.mark.asyncio
async def test_transport_invoke_executor_failed_exec_error(ssh_transport: SSHTransport):
    with subproc_coro_patch(retcode=0, stdout=FAILED_EXEC_MSG) as proc:
        messages = await ssh_transport.invoke("42", "executor.py", "TASK-ID")

    assert messages == [json.loads(FAILED_EXEC_MSG)]
    assert proc.call_count == 1


@pytest.mark.asyncio
async def test_transport_invoke_executor_exec_failed_system_error(
    ssh_transport: SSHTransport,
):
    with subproc_coro_patch(retcode=1, stdout=FAILED_SYSTEM_MSG) as proc:
        messages = await ssh_transport.invoke("42", "executor.py", "TASK-ID")

    assert messages == [json.loads(FAILED_SYSTEM_MSG)]
    assert proc.call_count == 1

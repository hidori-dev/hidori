import json
import sys
from unittest.mock import patch

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from hidori_runner.executors.remote import main as executor_main


@pytest.fixture(scope="function")
def mock_argv(request: pytest.FixtureRequest):
    with patch.object(sys, "argv", request.param):
        yield


@pytest.mark.parametrize("mock_argv", [["/hidori/executor.py"]], indirect=True)
@pytest.mark.usefixtures("mock_argv")
def test_executor_task_id_not_provided_error(capsys: pytest.CaptureFixture[str]):
    with pytest.raises(SystemExit):
        executor_main()

    assert json.loads(capsys.readouterr().out) == {
        "type": "error",
        "task": "system",
        "message": "internal error - invalid executor args",
    }


@pytest.mark.parametrize("mock_argv", [["/hidori/executor.py", "foo"]], indirect=True)
@pytest.mark.usefixtures("mock_argv")
def test_executor_task_id_invalid_error(capsys: pytest.CaptureFixture[str]):
    with pytest.raises(SystemExit):
        executor_main()

    assert json.loads(capsys.readouterr().out) == {
        "type": "error",
        "task": "system",
        "message": "internal error - requested task does not exist",
    }


@pytest.mark.parametrize("mock_argv", [["/hidori/executor.py", "foo"]], indirect=True)
@pytest.mark.usefixtures("mock_argv")
def test_executor_task_file_not_json_error(
    fs: FakeFilesystem, capsys: pytest.CaptureFixture[str]
):
    fs.create_file("/hidori/task-foo.json", contents="testing")
    with pytest.raises(SystemExit):
        executor_main()

    assert json.loads(capsys.readouterr().out) == {
        "type": "error",
        "task": "system",
        "message": "internal error - could not parse task file",
    }


@pytest.mark.parametrize("missing_field", ["name", "data", "module"])
@pytest.mark.parametrize("mock_argv", [["/hidori/executor.py", "foo"]], indirect=True)
@pytest.mark.usefixtures("mock_argv")
def test_executor_task_json_missing_required_fields_error(
    missing_field: str, fs: FakeFilesystem, capsys: pytest.CaptureFixture[str]
):
    data = {"name": "foo", "data": {"module": "bar", "param": "val"}}
    el = data["data"] if missing_field == "module" else data
    assert isinstance(el, dict)
    el.pop(missing_field)

    fs.create_file("/hidori/task-foo.json", contents=json.dumps(data))
    with pytest.raises(SystemExit):
        executor_main()

    assert json.loads(capsys.readouterr().out) == {
        "type": "error",
        "task": "system",
        "message": (
            f"internal error - invalid task structure: {{'{missing_field}': "
            "'value for required field not provided'}"
        ),
    }


@pytest.mark.parametrize("mock_argv", [["/hidori/executor.py", "foo"]], indirect=True)
@pytest.mark.usefixtures("mock_argv")
def test_executor_task_json_module_not_found_error(
    fs: FakeFilesystem, capsys: pytest.CaptureFixture[str]
):
    data = {"name": "foo", "data": {"module": "does-not-exist"}}

    fs.create_file("/hidori/task-foo.json", contents=json.dumps(data))
    with pytest.raises(SystemExit):
        executor_main()

    assert json.loads(capsys.readouterr().out) == {
        "type": "error",
        "task": "system",
        "message": "internal error - specified module does not exist",
    }


@pytest.mark.parametrize("mock_argv", [["/hidori/executor.py", "foo"]], indirect=True)
@pytest.mark.usefixtures("mock_argv")
@pytest.mark.usefixtures("example_module")
def test_executor_task_json_module_validation_error(
    fs: FakeFilesystem, capsys: pytest.CaptureFixture[str]
):
    data = {"name": "example", "data": {"module": "example", "error": "data"}}

    fs.create_file("/hidori/task-foo.json", contents=json.dumps(data))
    with pytest.raises(SystemExit):
        executor_main()

    assert json.loads(capsys.readouterr().out) == {
        "type": "error",
        "task": "example",
        "message": "action: value for required field not provided",
    }


@pytest.mark.parametrize("mock_argv", [["/hidori/executor.py", "foo"]], indirect=True)
@pytest.mark.usefixtures("mock_argv")
@pytest.mark.usefixtures("example_module")
def test_executor_task_json_module_execution_error(
    fs: FakeFilesystem, capsys: pytest.CaptureFixture[str]
):
    data = {"name": "example", "data": {"module": "example", "action": "error"}}

    fs.create_file("/hidori/task-foo.json", contents=json.dumps(data))
    with pytest.raises(SystemExit):
        executor_main()

    messages = capsys.readouterr().out.splitlines()
    assert len(messages) == 2
    assert json.loads(messages[0]) == {
        "type": "error",
        "task": "example",
        "message": "runtime error",
    }
    traceback_message = json.loads(messages[1])
    assert traceback_message["type"] == "error"
    assert traceback_message["task"] == "example"
    assert "Traceback (most recent call last)" in traceback_message["message"]
    assert "raise RuntimeError()" in traceback_message["message"]


@pytest.mark.parametrize("mock_argv", [["/hidori/executor.py", "foo"]], indirect=True)
@pytest.mark.usefixtures("mock_argv")
@pytest.mark.usefixtures("example_module")
def test_executor_task_json_module_execution_success(
    fs: FakeFilesystem, capsys: pytest.CaptureFixture[str]
):
    data = {"name": "example", "data": {"module": "example", "action": "ok"}}

    fs.create_file("/hidori/task-foo.json", contents=json.dumps(data))
    executor_main()

    assert json.loads(capsys.readouterr().out) == {
        "type": "success",
        "task": "example",
        "message": "ok",
    }

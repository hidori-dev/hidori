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

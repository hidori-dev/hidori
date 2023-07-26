import json
import pathlib
import sys
import traceback
from typing import NoReturn

from hidori_core.modules import MODULES_REGISTRY
from hidori_core.schema import Schema
from hidori_core.schema import errors as schema_errors
from hidori_core.utils import Messenger


class TaskDataSchema(Schema):
    module: str


class TaskSchema(Schema):
    name: str
    data: TaskDataSchema


def exit_with_error(sys_messenger: Messenger, message: str, code: int = 1) -> NoReturn:
    sys_messenger.queue_error(message)
    sys_messenger.flush()
    assert 0 <= code <= 255
    raise SystemExit(code)


def main() -> None:
    # TODO: Executor is not remote-specific but stdout (rename file to stdout.py)
    # TODO: Move executors to core - that's where they belong
    system_messenger = Messenger("system")
    if len(sys.argv) != 2:
        exit_with_error(system_messenger, "internal error - invalid executor args")

    root_path = pathlib.Path(sys.argv[0]).parent
    task_id = sys.argv[1]
    task_path = root_path / f"task-{task_id}.json"
    if not task_path.exists():
        exit_with_error(
            system_messenger, "internal error - requested task does not exist"
        )

    with open(task_path) as task_file:
        try:
            data = json.load(task_file)
        except json.JSONDecodeError:
            exit_with_error(
                system_messenger, "internal error - could not parse task file"
            )

    try:
        TaskSchema().validate(data)
    except schema_errors.SchemaError as e:
        exit_with_error(
            system_messenger, f"internal error - invalid task structure: {e}"
        )

    module = MODULES_REGISTRY.get(data["data"]["module"])
    if module is None:
        exit_with_error(
            system_messenger, "internal error - specified module does not exist"
        )

    task_messenger = Messenger(data["name"])
    module.validate(data["data"], task_messenger)
    if task_messenger.is_empty:
        try:
            module.execute(data["data"], task_messenger)
        except Exception as e:
            task_messenger.queue_error(
                "".join(traceback.format_exception(type(e), e, e.__traceback__))
            )
    has_error = task_messenger.has_errors
    task_messenger.flush()
    if has_error:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

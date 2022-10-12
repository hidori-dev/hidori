import json
import pathlib
import sys
import traceback

from hidori_core.modules import MODULES_REGISTRY
from hidori_core.utils import Messenger


def main() -> None:
    task_id = sys.argv[1]
    task_path = pathlib.Path(__file__).parent / f"task-{task_id}.json"
    with open(task_path) as task_file:
        data = json.load(task_file)

    # TODO: Add pre-flight env detection and verification
    # systemd
    # broaden access and lower reqs

    task_name = data["name"]
    task_data = data["data"]

    messenger = Messenger(task_name)
    module = MODULES_REGISTRY[task_data["module"]]
    module.validate(task_data, messenger)
    if messenger.is_empty:
        try:
            module.execute(task_data, messenger)
        except Exception as e:
            messenger.queue_error(
                "".join(traceback.format_exception(type(e), e, e.__traceback__))
            )
    messenger.flush()


if __name__ == "__main__":
    main()

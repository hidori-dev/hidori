import json
import pathlib
import sys

from hidori_core.modules import MODULES_REGISTRY
from hidori_core.utils import Messenger


def main():
    task_id = sys.argv[1]
    task_path = pathlib.Path(__file__).parent / f"task-{task_id}.json"
    with open(task_path) as task_file:
        data = json.load(task_file)

    # TODO: Add pre-flight env detection and verification
    # python >= 3.9
    # target python >= 3.7
    # systemd
    # broaden access and lower reqs

    task_name = data["name"]
    task_data = data["data"]

    messenger = Messenger(task_name)
    module = MODULES_REGISTRY[task_data["module"]]
    module.validate_and_execute(task_data, messenger)
    messenger.flush()

    # TODO: Summary of failed, affected and unaffected tasks


if __name__ == "__main__":
    main()

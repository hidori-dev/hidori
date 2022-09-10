import json
import pathlib

from hidori_core.modules import MODULES_REGISTRY
from hidori_core.utils import Messenger

RETURN_TO_INITIATOR_MODULES = ["file-push"]


def main():
    tasks_path = pathlib.Path(__file__).parent / "tasks.json"
    with open(tasks_path) as tasks_file:
        data = json.load(tasks_file)

    # TODO: Add pre-flight env detection and verification
    # python >= 3.9
    # target python >= 3.7
    # systemd
    # broaden access and lower reqs

    savefile_path = pathlib.Path(__file__).parent / ".savefile"
    starting_step = 0
    if savefile_path.exists():
        with savefile_path.open() as f:
            starting_step = int(f.read())

    for (step, (task, task_data)) in enumerate(data.items()):
        if step < starting_step:
            continue

        if step > starting_step:
            if task_data["module"] in RETURN_TO_INITIATOR_MODULES:
                with savefile_path.open("w") as f:
                    f.write(str(step))
                return

        module = MODULES_REGISTRY[task_data["module"]]
        messenger = Messenger(task)
        module.validate_and_execute(task_data, messenger)
        messenger.say_all()

    # TODO: Summary of failed, affected and unaffected tasks


if __name__ == "__main__":
    main()

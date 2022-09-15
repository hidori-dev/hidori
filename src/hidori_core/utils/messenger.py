import datetime
import json
from typing import List


class Messenger:
    def __init__(self, task_name: str) -> None:
        # TODO: probably going to run single task so bring back task to inits
        self._task: str = task_name
        self._messages: List[str] = []

    def queue(self, ty: str, time: str, message: str) -> None:
        self._messages.append(
            json.dumps(
                {
                    "type": ty,
                    "task": self._task,
                    "time": time,
                    "message": message,
                }
            )
        )

    def queue_success(self, message: str) -> None:
        now = datetime.datetime.now().time().strftime("%H:%M:%S")
        self.queue(ty="success", time=now, message=message)

    def queue_error(self, message: str) -> None:
        now = datetime.datetime.now().time().strftime("%H:%M:%S")
        self.queue(ty="error", time=now, message=message)

    def queue_affected(self, message: str) -> None:
        now = datetime.datetime.now().time().strftime("%H:%M:%S")
        self.queue(ty="affected", time=now, message=message)

    def queue_info(self, message: str) -> None:
        now = datetime.datetime.now().time().strftime("%H:%M:%S")
        self.queue(ty="info", time=now, message=message)

    def flush(self):
        while self._messages:
            print(self._messages.pop(0))

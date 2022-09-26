import json
from typing import List


class Messenger:
    def __init__(self, task_name: str) -> None:
        self._task: str = task_name
        self._messages: List[str] = []

    @property
    def is_empty(self) -> bool:
        return len(self._messages) == 0

    def queue(self, ty: str, message: str) -> None:
        self._messages.append(
            json.dumps(
                {
                    "type": ty,
                    "task": self._task,
                    "message": message,
                }
            )
        )

    def queue_success(self, message: str) -> None:
        self.queue(ty="success", message=message)

    def queue_error(self, message: str) -> None:
        self.queue(ty="error", message=message)

    def queue_affected(self, message: str) -> None:
        self.queue(ty="affected", message=message)

    def queue_info(self, message: str) -> None:
        self.queue(ty="info", message=message)

    def flush(self) -> None:
        while self._messages:
            print(self._messages.pop(0))

import json
from typing import Dict, List


class Messenger:
    def __init__(self, task_name: str) -> None:
        self._task: str = task_name
        self._messages: List[Dict[str, str]] = []

    @property
    def is_empty(self) -> bool:
        return len(self._messages) == 0

    @property
    def has_errors(self) -> bool:
        return any([m["type"] == "error" for m in self._messages])

    def queue(self, ty: str, message: str) -> None:
        self._messages.append(
            {
                "type": ty,
                "task": self._task,
                "message": message,
            }
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
            print(json.dumps(self._messages.pop(0)))

        self._messages = []

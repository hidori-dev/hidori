import datetime
from typing import List


class Colors:
    RED = "\033[31m"
    GREEN = "\033[32m"
    BLUE = "\033[34m"
    RESET = "\033[39m"


class Modifiers:
    BOLD = "\033[1m"
    RESET = "\033[0m"


class Messenger:
    def __init__(self) -> None:
        # TODO: user and host are hardcoded
        self._user = "root"
        self._host = "vm"
        self._task: str = ""
        self._messages: List[str] = []

    def set_task(self, task: str) -> None:
        self._task = task

    def queue_success(self, message: str) -> None:
        now = datetime.datetime.now().time().strftime("%H:%M:%S")
        self._messages.append(
            f"[{now}] {Modifiers.BOLD}{Colors.GREEN}"
            f"OK:{Colors.RESET}{Modifiers.RESET} {message}"
        )

    def queue_error(self, message: str) -> None:
        now = datetime.datetime.now().time().strftime("%H:%M:%S")
        self._messages.append(
            f"[{now}] {Modifiers.BOLD}{Colors.RED}"
            f"ERROR:{Colors.RESET}{Modifiers.RESET} {message}"
        )

    def queue_affected(self, message: str) -> None:
        now = datetime.datetime.now().time().strftime("%H:%M:%S")
        self._messages.append(
            f"[{now}] {Modifiers.BOLD}{Colors.BLUE}"
            f"AFFECTED:{Colors.RESET}{Modifiers.RESET} {message}"
        )

    def queue_info(self, message: str) -> None:
        now = datetime.datetime.now().time().strftime("%H:%M:%S")
        self._messages.append(
            f"[{now}] {Modifiers.BOLD}" f"INFO:{Modifiers.RESET} {message}"
        )

    def flush(self):
        print(
            f"{Modifiers.BOLD}[{self._user}@{self._host}: "
            f"{self._task}]{Modifiers.RESET}"
        )
        while self._messages:
            print(self._messages.pop(0))
        print()

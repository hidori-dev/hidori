import datetime
import importlib.metadata


class Colors:
    RED = "\033[31m"
    GREEN = "\033[32m"
    BLUE = "\033[34m"
    RESET = "\033[39m"


class Modifiers:
    BOLD = "\033[1m"
    RESET = "\033[0m"


COLOR_MAP = {
    "success": Colors.GREEN,
    "error": Colors.RED,
    "affected": Colors.BLUE,
    "info": "",
}

STATUS_MAP = {
    "success": "OK",
    "error": "ERROR",
    "affected": "AFFECTED",
    "info": "INFO",
}


def get_version():
    return importlib.metadata.version("hidori")


class ConsolePrinter:
    def __init__(self, *, user: str, target: str) -> None:
        self.user = user
        self.target = target

    def print_one(self, data: dict[str, str]) -> None:
        self._print_header(data["task"])
        self._print_entry(data["type"], data["message"])

    def print_all(self, data: list[dict[str, str]]) -> None:
        # TODO: Isn't it too naive?
        self._print_header(data[0]["task"])
        for entry_data in data:
            self._print_entry(entry_data["type"], entry_data["message"])

    def print_summary(self) -> None:
        print()

    def _print_header(self, task: str) -> None:
        print(f"{Modifiers.BOLD}[{self.user}@{self.target}: {task}]{Modifiers.RESET}")

    def _print_entry(self, message_type: str, message: str) -> None:
        curr_time = self._get_current_time()
        color = COLOR_MAP[message_type]
        status = STATUS_MAP[message_type]
        print(
            f"[{curr_time}] {Modifiers.BOLD}{color}{status}:"
            f"{Colors.RESET if color else ''}{Modifiers.RESET} {message}"
        )

    def _get_current_time(self) -> str:
        return datetime.datetime.now().strftime(r"%b %d %H:%M:%S")

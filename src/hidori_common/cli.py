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


class CLIMessageWriter:
    def __init__(self, *, user: str, target: str) -> None:
        self.user = user
        self.target = target

    def print_one(self, data: dict[str, str]) -> None:
        self._print_header(data["task"])
        self._print_entry(data["time"], data["type"], data["message"])

    def print_all(self, data: list[dict[str, str]]) -> None:
        # TODO: Isn't it too naive?
        self._print_header(data[0]["task"])
        for entry_data in data:
            self._print_entry(
                entry_data["time"], entry_data["type"], entry_data["message"]
            )

    def _print_header(self, task: str) -> None:
        print(f"{Modifiers.BOLD}[{self.user}@{self.target}: {task}]{Modifiers.RESET}")

    def _print_entry(self, time: str, message_type: str, message: str) -> None:
        color = COLOR_MAP[message_type]
        status = STATUS_MAP[message_type]
        print(
            f"[{time}] {Modifiers.BOLD}{color}{status}:"
            f"{Colors.RESET if color else ''}{Modifiers.RESET} {message}"
        )

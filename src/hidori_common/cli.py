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


class CLIMessageWriter:
    def __init__(self, *, user: str, target: str) -> None:
        self.user = user
        self.target = target

    def print(self, data: dict[str, str]) -> None:
        color = COLOR_MAP.get(data["type"])
        if color is None:
            raise RuntimeError(f"unrecognized message type: {data['type']}")

        output = (
            f"{Modifiers.BOLD}[{self.user}@{self.target}: "
            f"{data['task']}]{Modifiers.RESET}\n"
            f"[{data['time']}] {Modifiers.BOLD}{color}{data['type'].upper()}:"
            f"{Colors.RESET if color else ''}"
            f"{Modifiers.RESET} {data['message']}\n"
        )
        print(output)

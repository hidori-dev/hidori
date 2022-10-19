import json


def get_messages(
    output: str, transport_name: str, require_json: bool = True
) -> list[dict[str, str]]:
    messages_data: list[dict[str, str]] = []
    for message in output.splitlines():
        try:
            messages_data.append(json.loads(message))
        except json.JSONDecodeError:
            if require_json:
                continue
            messages_data.append(
                {
                    "type": "error",
                    "task": f"INTERNAL-{transport_name.upper()}-TRANSPORT",
                    "message": message,
                }
            )

    return messages_data

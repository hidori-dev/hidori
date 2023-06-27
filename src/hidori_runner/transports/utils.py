import json


def get_messages(
    output: str, transport_name: str, ignore_parse_error: bool = True
) -> list[dict[str, str]]:
    messages_data: list[dict[str, str]] = []
    for message in output.splitlines():
        try:
            messages_data.append(json.loads(message))
        except json.JSONDecodeError:
            # Usually we can safely ignore decode errors because it's just
            # some junk data that has nothing to do with our exchange.
            # However if anything failed in the transport we want to know.
            if not ignore_parse_error:
                messages_data.append(
                    {
                        "type": "error",
                        "task": f"INTERNAL-{transport_name.upper()}-TRANSPORT",
                        "message": message,
                    }
                )

    return messages_data

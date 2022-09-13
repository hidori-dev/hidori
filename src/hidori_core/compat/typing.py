# Kinda necessary because of Debian 10 which should be supported until June 2024,
# but since Python 3.7 will EOL around July 2023 hidori will drop Debian 10
# at that time as well.
# TODO: Remove in July 2023 when python 3.7 will probably EOL

# 3.8+:
try:
    from typing import Literal
# 3.7:
except ImportError:
    from typing_extensions import Literal  # type: ignore


__all__ = ["Literal"]

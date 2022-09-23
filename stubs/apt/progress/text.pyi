import io

from .base import OpProgress as BaseOpProgress

class OpProgress(BaseOpProgress):
    def __init__(self, outfile: io.TextIOBase) -> None: ...

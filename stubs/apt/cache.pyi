from .package import Package
from .progress.base import OpProgress

class Cache:
    def __init__(self, progress: OpProgress) -> None: ...
    def __getitem__(self, item: str) -> Package: ...
    def commit(self) -> None: ...

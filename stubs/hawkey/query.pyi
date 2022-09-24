from .package import Package

class Query:
    def installed(self) -> "Query": ...
    def filter(self, name: str) -> "Query": ...
    def run(self) -> list[Package]: ...
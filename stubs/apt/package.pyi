class Version:
    version: str

class Package:
    name: str
    is_installed: bool
    candidate: Version

    def mark_install(self) -> None: ...
    def mark_delete(self) -> None: ...

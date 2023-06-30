from hidori_core.modules.apt import AptModule
from hidori_core.modules.base import MODULES_REGISTRY
from hidori_core.modules.dnf import DnfModule
from hidori_core.modules.hello import HelloModule
from hidori_core.modules.hostname import HostnameModule
from hidori_core.modules.wait import WaitModule

__all__ = [
    "MODULES_REGISTRY",
    "AptModule",
    "DnfModule",
    "HelloModule",
    "HostnameModule",
    "WaitModule",
]

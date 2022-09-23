from typing import Any
from .proxies import ProxyObject

class SystemBus:
    def get_object(self, bus_name: str, object_path: str) -> ProxyObject: ...

class Interface:
    def __init__(self, object: ProxyObject, dbus_interface: str) -> None: ...
    def Get(self, interface_name: str, property_name: str) -> Any: ...
    def SetStaticHostname(self, hostname: str, interactive: bool) -> None: ...

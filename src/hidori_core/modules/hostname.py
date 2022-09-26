from typing import Dict

try:
    import dbus
except ImportError:
    ...

from hidori_core.modules.base import Module
from hidori_core.schema import Schema
from hidori_core.utils import Messenger

BUS_NAME = "org.freedesktop.hostname1"


class HostnameSchema(Schema):
    name: str


class HostnameModule(Module, name="hostname", schema_cls=HostnameSchema):
    def execute(self, validated_data: Dict[str, str], messenger: Messenger) -> None:
        assert dbus

        sysbus = dbus.SystemBus()
        hostnamed_proxy = sysbus.get_object(BUS_NAME, "/org/freedesktop/hostname1")

        dbus_iface = dbus.Interface(hostnamed_proxy, "org.freedesktop.DBus.Properties")
        old_hostname = dbus_iface.Get(BUS_NAME, "StaticHostname")
        new_hostname = validated_data["name"]
        if old_hostname == new_hostname:
            messenger.queue_success(f"hostname already set to {new_hostname}")
        else:
            # TODO: can only do that with escalated privileges
            hostname_iface = dbus.Interface(hostnamed_proxy, BUS_NAME)
            hostname_iface.SetStaticHostname(new_hostname, False)
            messenger.queue_affected(f"hostname changed to {new_hostname}")

from typing import Dict

import dbus

from hidori_core.modules.base import Module
from hidori_core.schema import Schema
from hidori_core.utils import Messenger


class HostnameSchema(Schema):
    name: str


class HostnameModule(Module, name="hostname", schema_cls=HostnameSchema):
    def execute(
        self, validated_data: Dict[str, str], messenger: Messenger
    ) -> Dict[str, str]:
        new_hostname = validated_data["name"]

        sysbus = dbus.SystemBus()
        hostnamed_proxy = sysbus.get_object(
            "org.freedesktop.hostname1", "/org/freedesktop/hostname1"
        )

        dbus_iface = dbus.Interface(hostnamed_proxy, "org.freedesktop.DBus.Properties")
        old_hostname = dbus_iface.Get("org.freedesktop.hostname1", "StaticHostname")
        if old_hostname == new_hostname:
            messenger.queue_success(f"hostname already set to {new_hostname}")
            return {"state": "unaffected"}

        hostname_iface = dbus.Interface(hostnamed_proxy, "org.freedesktop.hostname1")
        hostname_iface.SetStaticHostname(new_hostname, False)

        messenger.queue_affected(f"hostname changed to {new_hostname}")
        return {"state": "affected"}

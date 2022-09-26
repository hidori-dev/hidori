import io
from typing import Any, Dict, Optional

try:
    import apt
except ImportError:
    ...

from hidori_core.compat.typing import Literal
from hidori_core.modules.base import Module
from hidori_core.schema import Schema
from hidori_core.schema.constraints import Requires
from hidori_core.utils.messenger import Messenger

APT_STATE_INSTALLED = "installed"
APT_STATE_REMOVED = "removed"


def condition_state_requires_package(data: Dict[str, Any]) -> bool:
    return data.get("state") in [APT_STATE_INSTALLED, APT_STATE_REMOVED]


class AptSchema(Schema):
    state: Literal["upgraded", "installed", "removed"] = Requires(
        ["package"], data_conditions=[condition_state_requires_package]
    )
    package: Optional[str]


class AptModule(Module, name="apt", schema_cls=AptSchema):
    def execute(
        self, validated_data: Dict[str, Optional[str]], messenger: Messenger
    ) -> None:
        assert apt

        cache = apt.Cache(apt.progress.text.OpProgress(io.StringIO()))
        package_name = validated_data.get("package")

        if validated_data["state"] == APT_STATE_INSTALLED and package_name:
            apt_pkg = cache[package_name]
            if apt_pkg.is_installed:
                messenger.queue_success(f"package {package_name} is already installed")
                return

            messenger.queue_info(
                f"will install {apt_pkg.name} to version {apt_pkg.candidate.version}"
            )

            apt_pkg.mark_install()
            cache.commit()
            messenger.queue_affected(f"package {package_name} has been installed")
            return

        if validated_data["state"] == APT_STATE_REMOVED and package_name:
            apt_pkg = cache[package_name]
            if not apt_pkg.is_installed:
                messenger.queue_success(f"package {package_name} is not installed")
                return

            messenger.queue_info(f"will remove {apt_pkg.name}")

            apt_pkg.mark_delete()
            cache.commit()
            messenger.queue_affected(f"package {package_name} has been removed  ")
            return

        messenger.queue_error("internal error")

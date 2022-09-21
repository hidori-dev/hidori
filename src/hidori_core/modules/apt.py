import io
from typing import Any, Dict, Optional

try:
    import apt
except ImportError:
    apt = None

from hidori_core.compat.typing import Literal
from hidori_core.modules.base import Module
from hidori_core.schema import Schema
from hidori_core.schema.constraints import Requires
from hidori_core.utils.messenger import Messenger

APT_STATE_INSTALLED = "installed"


def condition_state_installed(data: Dict[str, Any]) -> bool:
    return data.get("state") == APT_STATE_INSTALLED


class AptSchema(Schema):
    state: Literal["upgraded", "installed"] = Requires(
        ["package"], data_conditions=[condition_state_installed]
    )
    package: Optional[str]


class AptModule(Module, name="apt", schema_cls=AptSchema):
    def execute(
        self, validated_data: Dict[str, Any], messenger: Messenger
    ) -> Dict[str, str]:
        cache = apt.Cache(apt.progress.text.OpProgress(io.StringIO()))
        package_name = validated_data.get("package")

        if validated_data["state"] == "installed":
            apt_pkg = cache[package_name]
            if apt_pkg.is_installed:
                messenger.queue_success(f"package {package_name} is already installed")
                return {"state": "unaffected"}

            messenger.queue_info(
                f"will install {apt_pkg.name} to version {apt_pkg.candidate.version}"
            )

            apt_pkg.mark_install()
            cache.commit()
            messenger.queue_affected(f"package {package_name} has been installed")
            return {"state": "affected"}

        messenger.queue_error("internal error")
        return {"state": "error"}

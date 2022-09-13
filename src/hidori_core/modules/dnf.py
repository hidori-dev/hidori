from typing import Any, Dict, Optional

try:
    import dnf
except ImportError:
    dnf = None

from hidori_core.compat.typing import Literal
from hidori_core.modules.base import Module
from hidori_core.schema.base import Schema
from hidori_core.schema.constraints import Requires
from hidori_core.utils import Messenger

DNF_STATE_INSTALLED = "installed"
DNF_STATE_UPGRADED = "upgraded"


def condition_require_package_if_state_installed(data: Dict[str, Any]) -> bool:
    return data.get("state") == DNF_STATE_INSTALLED


class DnfSchema(Schema):
    state: Literal["upgraded", "installed"] = Requires(
        ["package"], data_conditions=[condition_require_package_if_state_installed]
    )
    package: Optional[str]


class DnfModule(Module, name="dnf", schema_cls=DnfSchema):
    def execute(
        self, validated_data: Dict[str, Any], messenger: Messenger
    ) -> Dict[str, str]:
        base = dnf.Base()
        base.read_all_repos()
        base.fill_sack()
        package_name = validated_data.get("package")

        if validated_data["state"] == "installed":
            # TODO: Only allow package to be a list and name it packages
            # TODO: Verify that package exists in repos
            # TODO: Allow to provide version with `package:version` or
            # `package:latest` notation
            installed_query = base.sack.query().installed()
            if installed_query.filter(name=package_name):
                messenger.queue_success(f"package {package_name} is already installed")
                return {"state": "unaffected"}

            base.install(package_name)
            base.resolve()
            base.download_packages(base.transaction.install_set)

            for package in base.transaction.install_set:
                # TODO: verbose only, messenger should accept boolean parameter verbose
                messenger.queue_info(
                    f"will install {package.name} to version "
                    f"{package.version}-{package.release}"
                )

            base.do_transaction()
            messenger.queue_affected(f"package {package_name} has been installed")
            return {"state": "affected"}

        if validated_data["state"] == "upgraded" and package_name is None:
            base.upgrade_all()
            base.resolve()
            base.download_packages(base.transaction.install_set)

            if not base.transaction.install_set:
                messenger.queue_success("all packages are up to date")
                return {"state": "unaffected"}

            package_count = len(base.transaction.install_set)
            for package in base.transaction.install_set:
                # TODO: verbose only, messenger should accept boolean parameter verbose
                messenger.queue_info(
                    f"will upgrade {package.name} to version "
                    f"{package.version}-{package.release}"
                )

            base.do_transaction()
            messenger.queue_affected(f"performed upgrade of {package_count} packages")
            return {"state": "affected"}

        messenger.queue_error("internal error")
        return {"state": "error"}

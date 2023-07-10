from typing import Any, Dict, Literal, Optional

try:
    import dnf
except ImportError:
    ...

from hidori_core.modules.base import Module
from hidori_core.schema.base import Schema, define
from hidori_core.schema.modifiers import RequiresModifier
from hidori_core.utils import Messenger

DNF_STATE_INSTALLED = "installed"
DNF_STATE_UPGRADED = "upgraded"


def condition_state_installed(data: Dict[str, Any]) -> bool:
    return data.get("state") == DNF_STATE_INSTALLED


class DnfSchema(Schema):
    state: Literal["upgraded", "installed"] = define(
        modifiers=[
            RequiresModifier(["package"], data_conditions=[condition_state_installed])
        ]
    )
    package: Optional[str]


class DnfModule(Module, name="dnf", schema_cls=DnfSchema):
    def execute(
        self, validated_data: Dict[str, Optional[str]], messenger: Messenger
    ) -> None:
        assert dnf

        base = dnf.Base()
        base.read_all_repos()
        base.fill_sack()
        package_name = validated_data.get("package")

        if validated_data["state"] == "installed" and package_name:
            # TODO: Only allow package to be a list and name it packages
            # TODO: Verify that package exists in repos
            # TODO: Allow to provide version with `package:version` or
            # `package:latest` notation
            if base.sack.query().installed().filter(name=package_name).run():
                messenger.queue_success(f"package {package_name} is already installed")
                return

            # TODO: Handle package not existing (dnf.exceptions.PackageNotFoundError)
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
            return

        if validated_data["state"] == "upgraded" and package_name is None:
            base.upgrade_all()
            base.resolve()
            base.download_packages(base.transaction.install_set)

            if not base.transaction.install_set:
                messenger.queue_success("all packages are up to date")
                return

            package_count = len(base.transaction.install_set)
            for package in base.transaction.install_set:
                # TODO: verbose only, messenger should accept boolean parameter verbose
                messenger.queue_info(
                    f"will upgrade {package.name} to version "
                    f"{package.version}-{package.release}"
                )

            base.do_transaction()
            messenger.queue_affected(f"performed upgrade of {package_count} packages")
            return

        messenger.queue_error("internal error")

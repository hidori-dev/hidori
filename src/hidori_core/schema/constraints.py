from typing import Any, Callable, Dict, List, Optional, Type

from hidori_core.schema.base import Constraint, Schema
from hidori_core.schema.errors import ConstraintError

DataCondtion = Callable[[Dict[str, Any]], bool]


class RequiresConstraint(Constraint):
    def __init__(
        self,
        field_names: List[str],
        data_conditions: Optional[List[DataCondtion]] = None,
    ) -> None:
        self.required_field_names = set(field_names)
        self.data_conditions = data_conditions or []

    def process_schema(self, annotations: Dict[str, Any]) -> None:
        undefined_field_names = ", ".join(
            self.required_field_names.difference(annotations.keys())
        )
        if undefined_field_names:
            raise ConstraintError(
                f"fields named `{undefined_field_names}` "
                "might be required but are undefined"
            )

    def apply(self, schema: Type[Schema], data: Dict[str, Any]) -> None:
        # TODO: data_conditions should likely move to the Constraint base cls
        for condition in self.data_conditions:
            if not condition(data):
                return

        for field_name in self.required_field_names:
            schema.fields[field_name].required = True


def Requires(
    field_names: List[str], data_conditions: Optional[List[DataCondtion]] = None
) -> Any:
    return RequiresConstraint(field_names, data_conditions)

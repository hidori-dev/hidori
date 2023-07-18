from typing import Any, Dict, List, Optional

from hidori_core.schema.base import DataCondtion, Schema, SchemaModifier
from hidori_core.schema.errors import ModifierError


class RequiresModifier(SchemaModifier):
    def __init__(
        self,
        field_names: List[str],
        data_conditions: Optional[List[DataCondtion]] = None,
    ) -> None:
        self.required_field_names = set(field_names)
        self.data_conditions = data_conditions or []

    def process_schema(self, annotations: Dict[str, Any]) -> None:
        undefined_field_names = ", ".join(
            sorted(self.required_field_names.difference(annotations.keys()))
        )
        if undefined_field_names:
            raise ModifierError(
                f"fields named ({undefined_field_names}) "
                "might be required but are undefined"
            )

    def apply_to_schema(self, schema: Schema, data: Dict[str, Any]) -> None:
        for field_name in self.required_field_names:
            schema._internals_fields[field_name].required = True

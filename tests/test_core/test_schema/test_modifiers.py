from typing import Any, Literal

import pytest

from hidori_core.schema.base import DataCondtion, Schema, SchemaModifier
from hidori_core.schema.errors import ModifierError
from hidori_core.schema.modifiers import RequiresModifier


class SimpleModifier(SchemaModifier):
    def __init__(self, data_conditions: list[DataCondtion] | None = None) -> None:
        self.data_conditions = data_conditions or []

    def process_schema(self, annotations: dict[str, Any]) -> None:
        if "throw_error" in annotations:
            raise ModifierError()

    def apply_to_schema(self, schema: Schema, data: dict[str, Any]) -> None:
        if data["state"] == "modify":
            setattr(schema._internals_fields["a"], "modified", True)
            setattr(schema._internals_fields["b"], "modified", True)
        elif data["state"] == "restore":
            delattr(schema._internals_fields["a"], "modified")
            delattr(schema._internals_fields["b"], "modified")


class ErrorSchema(Schema):
    throw_error: str


class SimpleSchema(Schema):
    state: Literal["modify", "restore"]
    a: str
    b: str


class OptionalSchema(Schema):
    a: str
    b: str | None


def test_simple_modifier_throw_error_on_schema_processing():
    modifier = SimpleModifier()
    schema_annotations = ErrorSchema.__annotations__.copy()
    with pytest.raises(ModifierError):
        modifier.process_schema(ErrorSchema.__annotations__)
    assert schema_annotations == ErrorSchema.__annotations__


def test_simple_modifier_schema_update_and_restore():
    modifier = SimpleModifier()
    schema = SimpleSchema()
    schema_annotations = schema.__annotations__.copy()
    modifier.process_schema(schema.__annotations__)
    assert schema_annotations == schema.__annotations__
    modifier.apply(schema, {"state": "modify"})
    assert getattr(schema._internals_fields["a"], "modified") is True
    assert getattr(schema._internals_fields["b"], "modified") is True
    modifier.apply(schema, {"state": "restore"})
    assert hasattr(schema._internals_fields["a"], "modified") is False
    assert hasattr(schema._internals_fields["b"], "modified") is False


def test_simple_modifier_do_nothing_data_conditions():
    modifier = SimpleModifier(
        data_conditions=[
            lambda data: data.get("a") == "ok",
            lambda data: data.get("b") == "also-ok",
        ]
    )
    schema = SimpleSchema()
    schema_annotations = schema.__annotations__.copy()
    modifier.process_schema(schema.__annotations__)
    assert schema_annotations == schema.__annotations__
    modifier.apply(schema, {"state": "modify"})
    assert hasattr(schema._internals_fields["a"], "modified") is False
    assert hasattr(schema._internals_fields["b"], "modified") is False


def test_simple_modifier_do_nothing_partial_data_conditions():
    modifier = SimpleModifier(
        data_conditions=[
            lambda data: data.get("a") == "ok",
            lambda data: data.get("b") == "also-ok",
        ]
    )
    schema = SimpleSchema()
    schema_annotations = schema.__annotations__.copy()
    modifier.process_schema(schema.__annotations__)
    assert schema_annotations == schema.__annotations__
    modifier.apply(schema, {"state": "modify", "a": "ok"})
    assert hasattr(schema._internals_fields["a"], "modified") is False
    assert hasattr(schema._internals_fields["b"], "modified") is False


def test_simple_modifier_run_on_fulfilled_data_conditions():
    modifier = SimpleModifier(
        data_conditions=[
            lambda data: data.get("a") == "ok",
            lambda data: data.get("b") == "also-ok",
        ]
    )
    schema = SimpleSchema()
    schema_annotations = schema.__annotations__.copy()
    modifier.process_schema(schema.__annotations__)
    assert schema_annotations == schema.__annotations__
    modifier.apply(schema, {"state": "modify", "a": "ok", "b": "also-ok"})
    assert getattr(schema._internals_fields["a"], "modified") is True
    assert getattr(schema._internals_fields["b"], "modified") is True


def test_requires_modifier_fails_missing_fields():
    modifier = RequiresModifier(field_names=["a", "b"])
    schema_annotations = ErrorSchema.__annotations__.copy()
    with pytest.raises(ModifierError) as e:
        modifier.process_schema(ErrorSchema.__annotations__)
    assert schema_annotations == ErrorSchema.__annotations__
    assert str(e.value) == "fields named (a, b) might be required but are undefined"


def test_requires_modifier_do_nothing_data_conditions():
    modifier = RequiresModifier(
        field_names=["b"],
        data_conditions=[lambda data: data.get("a") == "ok"],
    )
    schema = OptionalSchema()
    schema_annotations = schema.__annotations__.copy()
    modifier.process_schema(schema.__annotations__)
    assert schema_annotations == schema.__annotations__
    modifier.apply(schema, {})
    assert schema._internals_fields["a"].required is True
    assert schema._internals_fields["b"].required is False


def test_requires_modifier_run_on_fulfilled_data_conditions():
    modifier = RequiresModifier(
        field_names=["b"],
        data_conditions=[lambda data: data.get("a") == "ok"],
    )
    schema = OptionalSchema()
    schema_annotations = schema.__annotations__.copy()
    modifier.process_schema(schema.__annotations__)
    assert schema_annotations == schema.__annotations__
    modifier.apply(schema, {"a": "ok"})
    assert schema._internals_fields["a"].required is True
    assert schema._internals_fields["b"].required is True
    # Undo the modifier
    schema._internals_fields["b"].required = False

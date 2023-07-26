from typing import Any, Dict, Literal

import pytest

from hidori_core.schema import errors as schema_errors
from hidori_core.schema import fields as schema_fields
from hidori_core.schema.base import FIELDS_REGISTRY, Field, Schema, _sentinel, define


class NestedSchema(Schema):
    bar: str


class SimpleSchema(Schema):
    foo: str
    nested: NestedSchema


class NestedSchemaWithDefault(Schema):
    bar: str = "example"


class SimpleSchemaWithDefault(Schema):
    foo: str = "example"
    nested: NestedSchemaWithDefault = define(default_factory=dict)


class SimpleField(Field):
    def __init__(self, required: bool) -> None:
        self.required = required

    @classmethod
    def from_annotation(cls, annotation: Any, required: bool = True) -> Any:
        return None


@pytest.fixture(scope="module")
def required_simple_field():
    return SimpleField(required=True)


@pytest.fixture(scope="module")
def optional_simple_field():
    return SimpleField(required=False)


def test_sanity_fields_registry_has_all_fields():
    assert FIELDS_REGISTRY == [
        schema_fields.Anything,
        schema_fields.Text,
        schema_fields.OneOf,
        schema_fields.SubSchema,
        schema_fields.Dictionary,
        SimpleField,
    ]


def test_field_validation_fail_sentinel_for_required(required_simple_field):
    with pytest.raises(schema_errors.ValidationError) as e:
        required_simple_field.validate(_sentinel)

    assert str(e.value) == "value for required field not provided"


def test_field_validation_skip_sentinel_for_optional(optional_simple_field):
    with pytest.raises(schema_errors.SkipFieldError):
        optional_simple_field.validate(_sentinel)


def test_field_validation_with_value_ok(required_simple_field, optional_simple_field):
    required_simple_field.validate(42)
    optional_simple_field.validate(42)


@pytest.mark.parametrize(
    "required,exc",
    [(True, schema_errors.ValidationError), (False, schema_errors.SkipFieldError)],
)
def test_anything_field_setup_and_validation(required, exc):
    assert schema_fields.Anything.from_annotation(str, required) is None
    assert schema_fields.Anything.from_annotation(int, required) is None
    assert schema_fields.Anything.from_annotation(Literal[42], required) is None
    assert schema_fields.Anything.from_annotation(Schema, required) is None
    assert schema_fields.Anything.from_annotation(SimpleSchema, required) is None

    field = schema_fields.Anything.from_annotation(Any, required)
    assert isinstance(field, schema_fields.Anything)
    assert field.required is required
    with pytest.raises(exc):
        field.validate(_sentinel)

    # Scenario: valid data
    assert field.validate(1) == 1
    assert field.validate(True) is True
    obj = object()
    assert field.validate(obj) == obj
    assert field.validate("foo") == "foo"


@pytest.mark.parametrize(
    "required,exc",
    [(True, schema_errors.ValidationError), (False, schema_errors.SkipFieldError)],
)
def test_text_field_setup_and_validation(required, exc):
    assert schema_fields.Text.from_annotation(Any, required) is None
    assert schema_fields.Text.from_annotation(int, required) is None
    assert schema_fields.Text.from_annotation(Literal[42], required) is None
    assert schema_fields.Text.from_annotation(Schema, required) is None
    assert schema_fields.Text.from_annotation(SimpleSchema, required) is None

    field = schema_fields.Text.from_annotation(str, required)
    assert isinstance(field, schema_fields.Text)
    assert field.required is required
    with pytest.raises(exc):
        field.validate(_sentinel)

    with pytest.raises(schema_errors.ValidationError) as e:
        field.validate(1)
    assert str(e.value) == "expected str, got int"
    with pytest.raises(schema_errors.ValidationError) as e:
        field.validate(True)
    assert str(e.value) == "expected str, got bool"
    with pytest.raises(schema_errors.ValidationError) as e:
        field.validate(object())
    assert str(e.value) == "expected str, got object"

    # Scenario: valid data
    assert field.validate("foo") == "foo"
    assert field.validate("") == ""


@pytest.mark.parametrize(
    "required,exc",
    [(True, schema_errors.ValidationError), (False, schema_errors.SkipFieldError)],
)
def test_oneof_field_setup_and_validation(required, exc):
    assert schema_fields.OneOf.from_annotation(Any, required) is None
    assert schema_fields.OneOf.from_annotation(int, required) is None
    assert schema_fields.OneOf.from_annotation(str, required) is None
    assert schema_fields.OneOf.from_annotation(Schema, required) is None
    assert schema_fields.OneOf.from_annotation(SimpleSchema, required) is None

    field = schema_fields.OneOf.from_annotation(Literal[42, "foo"], required)
    assert isinstance(field, schema_fields.OneOf)
    assert field.required is required
    with pytest.raises(exc):
        field.validate(_sentinel)

    with pytest.raises(schema_errors.ValidationError) as e:
        field.validate(1)
    assert str(e.value) == "not one of allowed values: (42, 'foo')"
    with pytest.raises(schema_errors.ValidationError) as e:
        field.validate(True)
    assert str(e.value) == "not one of allowed values: (42, 'foo')"
    with pytest.raises(schema_errors.ValidationError) as e:
        field.validate(object())
    assert str(e.value) == "not one of allowed values: (42, 'foo')"
    with pytest.raises(schema_errors.ValidationError) as e:
        field.validate("value")
    assert str(e.value) == "not one of allowed values: (42, 'foo')"

    # Scenario: valid data
    assert field.validate("foo") == "foo"
    assert field.validate(42) == 42


@pytest.mark.parametrize(
    "required,exc",
    [(True, schema_errors.ValidationError), (False, schema_errors.SkipFieldError)],
)
def test_schema_field_setup_and_validation(required, exc):
    assert schema_fields.SubSchema.from_annotation(Any, required) is None
    assert schema_fields.SubSchema.from_annotation(int, required) is None
    assert schema_fields.SubSchema.from_annotation(str, required) is None
    assert schema_fields.SubSchema.from_annotation(Schema, required) is None
    assert schema_fields.SubSchema.from_annotation(Literal[42, "foo"], required) is None

    field = schema_fields.SubSchema.from_annotation(SimpleSchema, required)
    assert isinstance(field, schema_fields.SubSchema)
    assert field.required is required
    with pytest.raises(exc):
        field.validate(_sentinel)

    with pytest.raises(schema_errors.ValidationError) as e:
        field.validate(1)
    assert str(e.value) == "expected dict, got int"
    with pytest.raises(schema_errors.ValidationError) as e:
        field.validate(True)
    assert str(e.value) == "expected dict, got bool"
    with pytest.raises(schema_errors.ValidationError) as e:
        field.validate(object())
    assert str(e.value) == "expected dict, got object"
    with pytest.raises(schema_errors.ValidationError) as e:
        field.validate("value")
    assert str(e.value) == "expected dict, got str"

    # Scenario: empty data is invalid for schema with required fields
    with pytest.raises(schema_errors.SchemaError) as e:
        field.validate({})
    assert e.value.errors == {
        "foo": "value for required field not provided",
        "nested": "value for required field not provided",
    }
    # Scenario: data with invalid value type and required field not provided
    with pytest.raises(schema_errors.SchemaError) as e:
        field.validate({"foo": 42})
    assert e.value.errors == {
        "foo": "expected str, got int",
        "nested": "value for required field not provided",
    }
    # Scenario: valid data for one field and empty data for the subschema
    with pytest.raises(schema_errors.SchemaError) as e:
        field.validate({"foo": "example", "nested": {}})
    assert e.value.errors == {
        "nested": {"bar": "value for required field not provided"}
    }
    # Scenario: valid data
    assert field.validate({"foo": "example", "nested": {"bar": "example"}}) == {
        "foo": "example",
        "nested": {"bar": "example"},
    }
    assert field.validate(
        {"foo": "example", "extra": "example", "nested": {"bar": "example"}}
    ) == {
        "foo": "example",
        "nested": {"bar": "example"},
    }
    assert field.validate(
        {"foo": "example", "nested": {"bar": "example", "extra": "example"}}
    ) == {
        "foo": "example",
        "nested": {"bar": "example"},
    }


@pytest.mark.parametrize(
    "required,exc",
    [(True, schema_errors.ValidationError), (False, schema_errors.SkipFieldError)],
)
def test_schema_with_default_field_setup_and_validation(required, exc):
    assert schema_fields.SubSchema.from_annotation(Any, required) is None
    assert schema_fields.SubSchema.from_annotation(int, required) is None
    assert schema_fields.SubSchema.from_annotation(str, required) is None
    assert schema_fields.SubSchema.from_annotation(Schema, required) is None
    assert schema_fields.SubSchema.from_annotation(Literal[42, "foo"], required) is None

    field = schema_fields.SubSchema.from_annotation(SimpleSchemaWithDefault, required)
    assert isinstance(field, schema_fields.SubSchema)
    assert field.required is required
    with pytest.raises(exc):
        field.validate(_sentinel)

    with pytest.raises(schema_errors.ValidationError) as e:
        field.validate(1)
    assert str(e.value) == "expected dict, got int"
    with pytest.raises(schema_errors.ValidationError) as e:
        field.validate(True)
    assert str(e.value) == "expected dict, got bool"
    with pytest.raises(schema_errors.ValidationError) as e:
        field.validate(object())
    assert str(e.value) == "expected dict, got object"
    with pytest.raises(schema_errors.ValidationError) as e:
        field.validate("value")
    assert str(e.value) == "expected dict, got str"

    # Scenario: valid data
    assert field.validate({}) == {"foo": "example", "nested": {"bar": "example"}}
    assert field.validate({"foo": "cool"}) == {
        "foo": "cool",
        "nested": {"bar": "example"},
    }
    assert field.validate({"nested": {"bar": "cool"}}) == {
        "foo": "example",
        "nested": {"bar": "cool"},
    }


@pytest.mark.parametrize("dict_type", [dict, Dict])
@pytest.mark.parametrize(
    "required,exc",
    [(True, schema_errors.ValidationError), (False, schema_errors.SkipFieldError)],
)
def test_dict_field_setup_and_validation(dict_type, required, exc):
    assert schema_fields.Dictionary.from_annotation(Any, required) is None
    assert schema_fields.Dictionary.from_annotation(int, required) is None
    assert schema_fields.Dictionary.from_annotation(str, required) is None
    assert schema_fields.Dictionary.from_annotation(Schema, required) is None
    assert (
        schema_fields.Dictionary.from_annotation(Literal[42, "foo"], required) is None
    )

    field = schema_fields.Dictionary.from_annotation(
        dict_type[str, dict_type[str, Literal[42, "foo"]]], required
    )
    assert isinstance(field, schema_fields.Dictionary)
    assert isinstance(field.key_field, schema_fields.Text)
    assert isinstance(field.val_field, schema_fields.Dictionary)
    assert isinstance(field.val_field.key_field, schema_fields.Text)
    assert isinstance(field.val_field.val_field, schema_fields.OneOf)
    assert field.required is required
    with pytest.raises(exc):
        field.validate(_sentinel)

    with pytest.raises(schema_errors.ValidationError) as e:
        field.validate(1)
    assert str(e.value) == "expected dict, got int"
    with pytest.raises(schema_errors.ValidationError) as e:
        field.validate(True)
    assert str(e.value) == "expected dict, got bool"
    with pytest.raises(schema_errors.ValidationError) as e:
        field.validate(object())
    assert str(e.value) == "expected dict, got object"
    with pytest.raises(schema_errors.ValidationError) as e:
        field.validate("value")
    assert str(e.value) == "expected dict, got str"

    # Scenario: invalid key and value data types
    with pytest.raises(schema_errors.ValidationError) as e:
        field.validate({13: "foo"})
    assert str(e.value) == "expected str, got int"
    # Scenario: invalid value data type
    with pytest.raises(schema_errors.ValidationError) as e:
        field.validate({"foo": "example"})
    assert str(e.value) == "expected dict, got str"
    # Scenario: invalid key and value data for nested dict
    with pytest.raises(schema_errors.ValidationError) as e:
        field.validate({"foo": {13: "example"}})
    assert str(e.value) == "expected str, got int"
    # Scenario: invalid value for the nested dict
    with pytest.raises(schema_errors.ValidationError) as e:
        field.validate({"foo": {"example": 13}})
    assert str(e.value) == "not one of allowed values: (42, 'foo')"
    # Scenario: invalid value for one of the nested dict values
    with pytest.raises(schema_errors.ValidationError) as e:
        field.validate({"foo": {"example": 42, "another": "bar"}})
    assert str(e.value) == "not one of allowed values: (42, 'foo')"
    # Scenario: valid data
    assert field.validate({}) == {}
    assert field.validate({"foo": {}}) == {"foo": {}}
    assert field.validate({"foo": {"example": 42}}) == {"foo": {"example": 42}}
    assert field.validate({"foo": {"example": 42, "another": "foo"}}) == {
        "foo": {"example": 42, "another": "foo"}
    }

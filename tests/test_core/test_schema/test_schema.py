from typing import Literal, Optional

import pytest

from hidori_core.schema import errors as schema_errors
from hidori_core.schema.base import Schema, define
from hidori_core.schema.modifiers import RequiresModifier


class EmptySchema(Schema):
    ...


class RequiredFieldSchema(Schema):
    a: str
    b: Literal["bar"]


class RequiresFieldSchema(Schema):
    a: Optional[str] = define(modifiers=[RequiresModifier(["b"])])
    b: Optional[str]


class MutuallyRequiredFieldsSchema(Schema):
    a: Optional[str] = define(modifiers=[RequiresModifier(["b"])])
    b: Optional[str] = define(modifiers=[RequiresModifier(["a"])])


class DefaultValueFieldsSchema(Schema):
    a: str = define(default="foo")
    b: str = define(default_factory=lambda: "bar")
    c: str = "car"


def test_schema_validation_error_missing_required_field():
    with pytest.raises(schema_errors.SchemaError) as e:

        class Foo(Schema):
            a: Optional[str] = define(modifiers=[RequiresModifier(["b"])])

    assert e.value.errors == {
        "a": ["fields named (b) might be required but are undefined"]
    }


def test_schema_error_used_internals_prefix():
    with pytest.raises(schema_errors.FieldNameNotAllowed) as e:

        class Foo(Schema):
            _internals_stuff: str

    assert str(e.value) == "_internals prefix is reserved for internal use"


def test_schema_field_unrecognized_annotation():
    with pytest.raises(schema_errors.UnrecognizedFieldType) as e:

        class Foo(Schema):
            a: object

    assert str(e.value) == "could not determine schema field for object type"


@pytest.mark.parametrize("data", [{}, {"foo": "bar"}])
def test_empty_schema_data_validation_anything_returns_empty(data):
    assert EmptySchema._internals_fields == {}
    assert EmptySchema().validate(data) == {}


def test_schema_data_validation_required_fields():
    assert RequiredFieldSchema().validate({"a": "foo", "b": "bar"}) == {
        "a": "foo",
        "b": "bar",
    }
    with pytest.raises(schema_errors.SchemaError) as e:
        assert RequiredFieldSchema().validate({})
    assert e.value.errors == {
        "a": "value for required field not provided",
        "b": "value for required field not provided",
    }
    with pytest.raises(schema_errors.SchemaError) as e:
        assert RequiredFieldSchema().validate({"a": 123, "b": "foo"})
    assert e.value.errors == {
        "a": "expected str, got int",
        "b": "not one of allowed values: ('bar',)",
    }


def test_schema_data_validation_requires_only_if_provided():
    assert RequiresFieldSchema().validate({}) == {}
    with pytest.raises(schema_errors.SchemaError) as e:
        RequiresFieldSchema().validate({"a": "foo"})
    assert e.value.errors == {"b": "value for required field not provided"}
    assert RequiresFieldSchema().validate({"a": "foo", "b": "bar"}) == {
        "a": "foo",
        "b": "bar",
    }
    assert RequiresFieldSchema().validate({"b": "bar"}) == {"b": "bar"}


def test_schema_data_validation_mutually_required_fields():
    assert MutuallyRequiredFieldsSchema().validate({}) == {}
    with pytest.raises(schema_errors.SchemaError) as e:
        MutuallyRequiredFieldsSchema().validate({"a": "foo"})
    assert e.value.errors == {"b": "value for required field not provided"}
    with pytest.raises(schema_errors.SchemaError) as e:
        MutuallyRequiredFieldsSchema().validate({"b": "bar"})
    assert e.value.errors == {"a": "value for required field not provided"}
    assert MutuallyRequiredFieldsSchema().validate({"a": "foo", "b": "bar"}) == {
        "a": "foo",
        "b": "bar",
    }


def test_schema_data_validation_default_fields():
    assert DefaultValueFieldsSchema().validate({}) == {
        "a": "foo",
        "b": "bar",
        "c": "car",
    }
    assert DefaultValueFieldsSchema().validate({"a": "example"}) == {
        "a": "example",
        "b": "bar",
        "c": "car",
    }
    assert DefaultValueFieldsSchema().validate({"b": "example"}) == {
        "a": "foo",
        "b": "example",
        "c": "car",
    }
    assert DefaultValueFieldsSchema().validate({"c": "example"}) == {
        "a": "foo",
        "b": "bar",
        "c": "example",
    }

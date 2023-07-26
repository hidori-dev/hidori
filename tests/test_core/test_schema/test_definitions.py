from unittest.mock import Mock, call

import pytest

from hidori_core.schema import errors as schema_errors
from hidori_core.schema.base import Definition, _sentinel, define


def test_schema_define_without_arguments():
    definition: Definition = define()
    assert definition.modifiers == []
    assert definition.default == _sentinel
    assert definition.default_factory is None
    assert definition._field_name is None
    assert definition.errors == []


@pytest.mark.parametrize("modifiers", ([], [Mock()]))
@pytest.mark.parametrize("default", (None, "example"))
@pytest.mark.parametrize("default_factory", (None, Mock()))
def test_schema_define_with_arguments(modifiers, default, default_factory):
    if default is not _sentinel and default_factory:
        with pytest.raises(schema_errors.MultipleDefaultMethodsError):
            define(modifiers, default, default_factory)
    else:
        definition: Definition = define(modifiers, default, default_factory)
        assert definition.modifiers == modifiers
        assert definition.default == default
        assert definition.default_factory == default_factory
        assert definition._field_name is None
        assert definition.errors == []


def test_schema_definition_assign_field_name():
    definition: Definition = define()
    assert definition._field_name is None
    definition.field_name = "example"
    assert definition._field_name == "example"


def test_schema_definition_cannot_reassign_field_name():
    definition: Definition = define()
    assert definition._field_name is None
    definition.field_name = "example"
    with pytest.raises(schema_errors.DefinitionAlreadyAssigned):
        definition.field_name = "another"
    assert definition._field_name == "example"


@pytest.mark.parametrize("modifiers", ([], [Mock()], [Mock(), Mock()]))
def test_schema_definition_validate_modifiers_no_error(modifiers):
    definition: Definition = define(modifiers)
    annotations = {"a": str, "b": int}
    definition.validate_modifiers(annotations)
    assert annotations == {"a": str, "b": int}
    for modifier in modifiers:
        expected = [call.process_schema(annotations)]
        assert modifier.mock_calls == expected
    assert definition.errors == definition._errors
    assert definition.errors == []


@pytest.mark.parametrize(
    "modifiers",
    (
        [Mock(process_schema=Mock(side_effect=schema_errors.ModifierError("first")))],
        [
            Mock(process_schema=Mock(side_effect=schema_errors.ModifierError("first"))),
            Mock(
                process_schema=Mock(side_effect=schema_errors.ModifierError("second"))
            ),
        ],
    ),
)
def test_schema_definition_validate_modifiers_with_error(modifiers):
    definition: Definition = define(modifiers)
    annotations = {"a": str, "b": int}
    definition.validate_modifiers(annotations)
    assert annotations == {"a": str, "b": int}
    for modifier in modifiers:
        expected = [call.process_schema(annotations)]
        assert modifier.mock_calls == expected
    assert definition.errors == definition._errors
    expected_errors = ["first"] if len(modifiers) == 1 else ["first", "second"]
    assert definition.errors == expected_errors


@pytest.mark.parametrize("modifiers", ([], [Mock()], [Mock(), Mock()]))
@pytest.mark.parametrize("field_name", ["a", "b"])
def test_schema_definition_applies_all_modifiers(modifiers, field_name):
    definition: Definition = define(modifiers)
    definition.field_name = field_name
    schema = Mock()
    data = {"a": "example", "b": 13}
    definition.apply_modifiers(schema, data)
    assert data == {"a": "example", "b": 13}
    for modifier in modifiers:
        expected = [call.apply(schema, data)]
        assert modifier.mock_calls == expected
        modifier.reset_mock()


@pytest.mark.parametrize("modifiers", ([], [Mock()], [Mock(), Mock()]))
@pytest.mark.parametrize("field_name", ["c", "d"])
def test_schema_definition_applies_no_modifiers(modifiers, field_name):
    definition: Definition = define(modifiers)
    definition.field_name = field_name
    data = {"a": "example", "b": 13}
    definition.apply_modifiers(Mock(), data)
    assert data == {"a": "example", "b": 13}
    for modifier in modifiers:
        assert modifier.mock_calls == []


@pytest.mark.parametrize(
    "kwargs", [{"default": "example"}, {"default_factory": lambda: "example"}]
)
def test_schema_definition_apply_default_no_field_name(kwargs):
    definition: Definition = define(**kwargs)
    data = {"a": "example", "b": 13}
    with pytest.raises(AssertionError):
        definition.apply_default(data)
    assert data == {"a": "example", "b": 13}


@pytest.mark.parametrize("field_name", ["a", "b", "c", "d"])
def test_schema_definition_apply_default_no_method(field_name):
    definition: Definition = define()
    definition.field_name = field_name
    data = {"a": "example", "b": 13}
    definition.apply_default(data)
    assert data == {"a": "example", "b": 13}


@pytest.mark.parametrize(
    "kwargs", [{"default": "example"}, {"default_factory": lambda: "example"}]
)
@pytest.mark.parametrize("field_name", ["a", "b"])
def test_schema_definition_apply_default_dont_override(kwargs, field_name):
    definition: Definition = define(**kwargs)
    definition.field_name = field_name
    data = {"a": "example", "b": 13}
    definition.apply_default(data)
    assert data == {"a": "example", "b": 13}


@pytest.mark.parametrize(
    "kwargs", [{"default": "example"}, {"default_factory": lambda: "example"}]
)
@pytest.mark.parametrize("field_name", ["c", "d"])
def test_schema_definition_apply_default_not_in_data(kwargs, field_name):
    definition: Definition = define(**kwargs)
    definition.field_name = field_name
    data = {"a": "example", "b": 13}
    definition.apply_default(data)
    assert data == {"a": "example", "b": 13, field_name: "example"}

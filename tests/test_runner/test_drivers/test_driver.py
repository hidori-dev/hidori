import pytest

from hidori_core.schema.errors import SchemaError
from hidori_runner.drivers.base import Driver


def test_driver_empty_config_init_error(example_driver_cls: type[Driver]):
    with pytest.raises(SchemaError) as e:
        example_driver_cls(config={})

    assert e.value.errors == {"value": "value for required field not provided"}


def test_driver_invalid_config_init_error(example_driver_cls: type[Driver]):
    with pytest.raises(SchemaError) as e:
        example_driver_cls(config={"value": 42})

    assert e.value.errors == {"value": "value `42` not allowed; is not str"}


def test_driver_init_success(example_driver_cls: type[Driver]):
    driver = example_driver_cls(config={"value": "42"})
    assert getattr(driver, "value") == "42"

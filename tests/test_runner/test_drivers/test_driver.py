from unittest.mock import Mock

import pytest

from hidori_core.schema.errors import SchemaError
from hidori_runner.drivers.base import Driver
from hidori_runner.drivers.utils import create_pipeline_dir


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
    assert driver.user == "example-user"
    assert driver.target_id == "example-target"


@pytest.mark.usefixtures("mock_uuid", "setup_filesystem")
def test_driver_prepare_pipeline_dir_exists_error(example_driver: Driver):
    create_pipeline_dir(example_driver.target_id)
    with pytest.raises(FileExistsError):
        example_driver.prepare(Mock())

from unittest.mock import Mock

import pytest

from hidori_core.schema.errors import SchemaError
from hidori_pipelines.pipeline import Pipeline
from hidori_runner.drivers.base import DRIVERS_REGISTRY, Driver, create_driver
from hidori_runner.drivers.utils import create_pipeline_dir, get_pipelines_path


def test_driver_empty_config_init_error(example_driver_cls: type[Driver]):
    with pytest.raises(SchemaError) as e:
        example_driver_cls(config={})

    assert e.value.errors == {"value": "value for required field not provided"}


def test_driver_invalid_config_init_error(example_driver_cls: type[Driver]):
    with pytest.raises(SchemaError) as e:
        example_driver_cls(config={"value": 42})

    assert e.value.errors == {"value": "expected str, got int"}


def test_driver_init_success(example_driver_cls: type[Driver]):
    driver = example_driver_cls(config={"value": "42"})
    assert getattr(driver, "value") == "42"
    assert driver.user == "example-user"
    assert driver.target == "example-target"


def test_driver_create_not_found_error():
    with pytest.raises(KeyError):
        create_driver(destination_data={"driver": "not-existing"})


def test_driver_create_default_ssh_driver_success():
    driver = create_driver(destination_data={"target": "127.0.0.1", "user": "foo"})
    assert isinstance(driver, DRIVERS_REGISTRY["ssh"])


def test_driver_create_example_driver_success(example_driver_cls: type[Driver]):
    driver = create_driver(destination_data={"driver": "example", "value": "42"})
    assert isinstance(driver, DRIVERS_REGISTRY["example"])


@pytest.mark.usefixtures("mock_uuid", "setup_filesystem")
def test_driver_prepare_pipeline_dir_exists_error(example_driver: Driver):
    create_pipeline_dir("42", example_driver.target)
    with pytest.raises(FileExistsError):
        example_driver.prepare_pipeline(Mock())


@pytest.mark.usefixtures("mock_uuid", "setup_filesystem")
def test_driver_prepare_pipeline_success(
    example_driver: Driver, example_pipeline: Pipeline
):
    exchange = example_driver.prepare_pipeline(example_pipeline)
    assert not exchange.has_errors
    assert exchange.messages == []
    expected_localpath = get_pipelines_path() / "example-target/hidori-42"
    assert exchange.localpath == expected_localpath
    assert exchange.transport.name == "example"

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

    assert e.value.errors == {"value": "value `42` not allowed; is not str"}


def test_driver_init_success(example_driver_cls: type[Driver]):
    driver = example_driver_cls(config={"value": "42"})
    assert getattr(driver, "value") == "42"
    assert driver.user == "example-user"
    assert driver.target_id == "example-target"


def test_driver_create_not_found_error():
    with pytest.raises(KeyError):
        create_driver(target_data={"driver": "not-existing"})


def test_driver_create_default_ssh_driver_success():
    driver = create_driver(target_data={"ip": "127.0.0.1", "user": "foo"})
    assert isinstance(driver, DRIVERS_REGISTRY["ssh"])


def test_driver_create_example_driver_success(example_driver_cls: type[Driver]):
    driver = create_driver(target_data={"driver": "example", "value": "42"})
    assert isinstance(driver, DRIVERS_REGISTRY["example"])


@pytest.mark.usefixtures("mock_uuid", "setup_filesystem")
def test_driver_prepare_pipeline_dir_exists_error(example_driver: Driver):
    create_pipeline_dir(example_driver.target_id)
    with pytest.raises(FileExistsError):
        example_driver.prepare(Mock())


@pytest.mark.usefixtures("mock_uuid", "setup_filesystem")
def test_driver_prepare_pipeline_success(
    example_driver: Driver, example_pipeline: Pipeline
):
    prepared_pipeline = example_driver.prepare(example_pipeline)
    assert not prepared_pipeline.has_errors
    assert prepared_pipeline.messages == []
    expected_localpath = get_pipelines_path() / "example-target/hidori-42"
    assert prepared_pipeline.localpath == expected_localpath
    assert prepared_pipeline.transport.name == "example"

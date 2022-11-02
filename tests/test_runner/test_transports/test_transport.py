import os
from typing import Any

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from hidori_common.typings import Transport


@pytest.mark.usefixtures("fs")
def test_transport_push_file_does_not_exist_error(example_transport: Transport[Any]):
    messages = example_transport.push("/foo/hidori")
    assert messages == [
        {
            "type": "error",
            "task": "INTERNAL-EXAMPLE-TRANSPORT",
            "message": "file not found",
        }
    ]


def test_transport_pushed_file_no_read_error(
    example_transport: Transport[Any], fs: FakeFilesystem
):
    fs.create_file("/foo/hidori", contents="data")
    os.chmod("/foo/hidori", 0o000)

    messages = example_transport.push("/foo/hidori")
    assert messages == [
        {
            "type": "error",
            "task": "INTERNAL-EXAMPLE-TRANSPORT",
            "message": "no permission",
        }
    ]


def test_transport_pushed_file_read_ok(
    example_transport: Transport[Any], fs: FakeFilesystem
):
    fs.create_file("/foo/hidori", contents="data")
    messages = example_transport.push("/foo/hidori")
    assert messages == []

    with open("/example/hidori") as f:
        assert f.read() == "data"


@pytest.mark.usefixtures("fs")
def test_transport_invoke_file_does_not_exist_error(example_transport: Transport[Any]):
    messages = example_transport.invoke("/example/hidori", [])
    assert messages == [
        {
            "type": "error",
            "task": "INTERNAL-EXAMPLE-TRANSPORT",
            "message": "file not found",
        }
    ]


def test_transport_invoke_no_file_permission_error(
    example_transport: Transport[Any], fs: FakeFilesystem
):
    fs.create_file("/example/hidori", contents="data")
    os.chmod("/example/hidori", 0o000)

    messages = example_transport.invoke("/example/hidori", [])
    assert messages == [
        {
            "type": "error",
            "task": "INTERNAL-EXAMPLE-TRANSPORT",
            "message": "no permission",
        }
    ]


def test_transport_invoke_success_ok(
    example_transport: Transport[Any], fs: FakeFilesystem
):
    fs.create_file("/example/hidori", contents="data")
    messages = example_transport.invoke("/example/hidori", ["upper"])
    assert messages == [{"type": "success", "task": "example", "message": "DATA-42"}]

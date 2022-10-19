import os
from typing import Any

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from hidori_common.typings import Transport


@pytest.mark.usefixtures("fs")
def test_transport_push_file_does_not_exist_error(example_transport: Transport[Any]):
    messages = example_transport.push("/foo/source", "/bar/dest")
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
    fs.create_file("/foo/source", contents="data")
    os.chmod("/foo/source", 0o000)

    messages = example_transport.push("/foo/source", "/bar/dest")
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
    fs.create_file("/foo/source", contents="data")
    messages = example_transport.push("/foo/source", "/bar/dest")
    assert messages == []

    with open("/bar/dest") as f:
        assert f.read() == "data"


@pytest.mark.usefixtures("fs")
def test_transport_invoke_file_does_not_exist_error(example_transport: Transport[Any]):
    messages = example_transport.invoke("/bar/dest", [])
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
    fs.create_file("/bar/dest", contents="data")
    os.chmod("/bar/dest", 0o000)

    messages = example_transport.invoke("/bar/dest", [])
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
    fs.create_file("/bar/dest", contents="data")
    messages = example_transport.invoke("/bar/dest", ["upper"])
    assert messages == [{"type": "success", "task": "example", "message": "DATA"}]

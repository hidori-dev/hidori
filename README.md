# Hidori

[![PyPI](https://img.shields.io/pypi/v/hidori)](https://pypi.org/project/hidori/)
[![CI](https://github.com/hidori-dev/hidori/actions/workflows/ci.yml/badge.svg)](https://github.com/hidori-dev/hidori/actions/workflows/ci.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/hidori-dev/hidori)

Hidori is a modern, agentless, zero-dependency[^1] variation on updating system state. General rule of thumb is that changes to the system are only done if the requested state is different from the actual state. Hidori modules are idempotent if the system is already in the desired state.
Every change in the destination system is reported through the modules log as "affected".

Hidori communicates with destination machines through appropriate protocol that is designated by the chosen driver.

![Hidori demo](https://raw.githubusercontent.com/hidori-dev/hidori/main/assets/hidori_demo.gif)

## Install

Depending on your environment you might wish to install Hidori globally or locally using chosen Python dependency manager such as poetry or pip.
Ultimately, the choice is yours. Either way, Hidori is safe for your Python environment - it does not pull any dependencies from PyPI.

Example using pip:
```sh
pip install hidori
```

## Hello World

With Hidori installed you need a single TOML file that provides where and what should be done. A simple 'hello world' example assuming that some machine is available at the given target:

```toml
[destinations]

  [destinations.vm]
  target = "192.168.122.31"
  user = "root"

[tasks]

  [tasks."Say hello"]
  module = "hello"
```

Now you just need to run it (example assumes the file is named `pipeline.toml`):

```sh
hidori-pipeline run pipeline.toml
```

The result on my machine is:

```
[root@vm: Say hello]
[16:03:19] OK: Hello from Linux debian 4.19.0-21-amd64
```

## Support

In general, Hidori is based on Python 3.11, but `hidori_core` runs with any version of Python that is still supported.
Reason for that is vast majority of destination systems don't have the latest Python runtime installed, so therefore `hidori_core`
which includes all the code that runs on a destination system can be expected to be supported according to the following table:

| Python Version |     EOL Date     |
| -------------- | ---------------- |
| 3.8            | November 2024    |
| 3.9            | November 2025    |
| 3.10           | November 2026    |
| 3.11           | November 2027(?) |

## Development

The dev environment can be setup with poetry:
```sh
poetry install
```

[^1]: Except for the necessary runtime - python, and system libraries that are used by modules

## License

Hidori is licensed under both the [MIT](LICENSE-MIT) and the [EUPL-1.2](LICENSE-EUPL) licenses.

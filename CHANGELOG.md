# Change Log

## [Unreleased]

## [0.1.0] - 2022-09-13

Initial release that contains proof-of-concept implementation.

### Added
- project structure and definition with pyproject.toml via poetry
- hidori_cli: entrypoint to Pipelines provided as hidori-pipelines command
- hidori_core: Pipelines interface with hardcoded SSH
- hidori_core: basic schema features for sake of modules
- hidori_core: PoC implementation of hello module
- hidori_core: PoC implementation of dnf module
- hidori_core: PoC implementation of hostname module
- hidori_core: simple messenger that provides colored output
- hidori_runner: remote executor that is capable of running modules 

[Unreleased]: https://github.com/hidori-dev/hidori/compare/0.1.0...HEAD
[0.1.0]: https://github.com/hidori-dev/hidori/releases/tag/0.1.0
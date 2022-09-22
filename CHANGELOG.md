# Change Log

## [Unreleased]

## [0.2.0] - 2022-09-22

Another pre-alpha release with many improvements on the core and a new APT module.

### Added
- APT module that can install a designated package.
- Schema validation for loaded pipelines TOML input.
- Ability to run a given pipeline on multiple hosts.
- More sophisticated validation with new Anything, Dictionary and SubSchema fields.

### Changed
- Relicense under dual licensing made of MIT and EUPL-1.2.
- Modules now write JSON to stdout which is then consumed by CLI output writer.
- Remote executor now runs a single task based on provided parameter.
- Package metadata is provided for better PyPI experience.

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
[0.2.0]: https://github.com/hidori-dev/hidori/releases/tag/0.2.0

# Change Log

## [Unreleased]

## [0.3.0] - 2023-06-28

Next iteration of alpha-state features, bugfixes and quality of life improvements.
So far not tested very thoroughly and missing coverage, but should work for happy paths.
Significant part of the effort went into the CLI and the framework should be good enough for future requirements.
Huge number of breaking changes since the previous release, but there is no reason for backwards-compatibility effort at this stage of development.

### Added
- New "hidori" command that allows to issue "calls", i.e. to run a single module using ssh-like syntax.
- Introduce idea of an "exchange" that exposes details such as ID used to recognize what to run, path to the local directory that contains pipeline/call data, transport object that allows to communicate with the destination and messages received from the remote.
- CLI fields that allow to define custom actions based on a field name or field type gathered from typehint.
- Define special CLI fields for version that displays version information, and extra_data that contains any data that wasn't parsed by other fields.
- Define boolean field for bool type, filepath field for path type and text field for string type.
- Support for the removal of installed packages for APT module.
- Stub Dockerfile for experiments and to have an option for systems that don't have a possibility to run Python 3.11+.
- Basic testing infrastructure such as fixtures along with incomplete tests for drivers, transports and remote executor.

### Changed
- Support for Python 3.7 for the core is dropped along with compatibility code and typing-extensions dependency, and 3.8 is the minimal required Python on targets.
- For better consistency some of the concepts were renamed. The result is that the description of target and means to access it (usually user) is now called "destination" and "target" is the identification of the remote machine (e.g. IP address/hostname). Also unify drivers, transports which used different names such as "target_id" or "ip" with common name "target".
- Decouple drivers and transports from pipelines to allow for easier integration with calls.
- Refactor SSH transport to provide standard interface with push and invoke methods.
- Modules no longer return state dictionary as the information is contained in the queued messenger entries.
- Validate provided tasks data using schema in the remote executor to gain confidence about its structure.
- Gather information about any errors in executor using a dedicated system messenger.
- Place prepared exchange files in appropriate user cache directory instead of a temp directory.
- Include month and day in the timestamp for exchange log entries.
- Rename CLIMessageWriter to ConsolePrinter for clarity.
- Provide missing toolchain setup for mypy, pytest, coverage and pre-commit.
- Update all the development dependencies to the latest possible versions.
- Move from pre-commit.ci to common Github Actions job.

### Fixed
- Crashes in the CLI caused by unhandled scenarios such as a command without any subparsers or optional fields.
- Many typing problems and issues reported by other linters.

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

[Unreleased]: https://github.com/hidori-dev/hidori/compare/0.3.0...HEAD
[0.1.0]: https://github.com/hidori-dev/hidori/releases/tag/0.1.0
[0.2.0]: https://github.com/hidori-dev/hidori/releases/tag/0.2.0
[0.3.0]: https://github.com/hidori-dev/hidori/releases/tag/0.3.0

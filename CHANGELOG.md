# Changelog

All notable changes to this project will be documented in this file. The format
is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and the
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- Simplify setup of zip format for `sdist` command using `setup.cfg`.
- Fix missing opening modes with `io.open` in `setup.py` file.

## [1.4.0] - 2022-02-03

### Added
- Support for Python 3.10.

### Changed
- Split lint and test requirements into two separate files.
- Upgrade lint and test requirements where possible.
- Set default source distribution format to zip.

### Fixed
- Fix setup encoding comment to deal with corner case under PowerShell.
- Fix missing requirement files in source distribution that were making
  the `setup.py` unusable.

## [1.3.0] - 2020-12-09

### Fixed
- Fix missing classifier for Python 2.6.
- Fix encoding issue when reading/writing the files inside the wheel
  `dist-info` folder.
- Fix access to `wheelbin` with module syntax, i.e. `python -m wheelbin`.

## [1.2.0] - 2020-12-08

### Added
- Option `--quiet` to prevent `wheelbin` from writing to stdout.

### Changed
- Reorganise the internal library structure with object-oriented paradigm.
- Rename option `--ignore` into `--exclude`.

## [1.1.0] - 2020-11-17

### Added
- Support for Python 3.
- Option `--ignore` to skip compilation for a given wildcard pattern.

## [1.0.0] - 2016-09-25

### Added
- Initial release.


[Unreleased]:
https://github.com/molinav/wheelbin/compare/v1.4.0..develop
[1.4.0]:
https://github.com/molinav/wheelbin/compare/v1.3.0..v1.4.0
[1.3.0]:
https://github.com/molinav/wheelbin/compare/v1.2.0..v1.3.0
[1.2.0]:
https://github.com/molinav/wheelbin/compare/v1.1.0..v1.2.0
[1.1.0]:
https://github.com/molinav/wheelbin/compare/v1.0.0..v1.1.0
[1.0.0]:
https://github.com/molinav/wheelbin/tree/v1.0.0

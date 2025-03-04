# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2024-03-03

### Fixed
- Fixed issue with RecordCounter and TextAppender processors not writing to output files
- Added proper implementation of the `finalize` method in RecordCounter to write record count to output
- Ensured all processors correctly handle output streams
- Fixed test for ProcessorFactory to use the correct processor type name

## [0.1.1] - 2024-03-02

### Added
- Initial release with basic functionality
- Support for fixed-length and delimited file formats
- Configurable validation rules
- YAML and string-based configuration options 
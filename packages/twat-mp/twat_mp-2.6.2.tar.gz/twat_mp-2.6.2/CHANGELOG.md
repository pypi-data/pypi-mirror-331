# Changelog

All notable changes to the `twat-mp` project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Created comprehensive API reference documentation
- Added architecture diagrams explaining component relationships and workflows
- Added real-world examples for image processing, data processing, web scraping, and file operations
- Implemented better error handling with descriptive error messages and suggestions
- Added interactive examples in Jupyter notebooks
- Implemented debug mode with detailed logging

### Changed

- Improved resource cleanup in AsyncMultiPool.__aexit__ using close() instead of terminate()
- Enhanced error handling during pool cleanup to ensure proper resource management
- Updated docstrings with more examples and clearer explanations
- Improved compatibility with Python 3.12+ async features
- Enhanced exception propagation from worker processes
- Fixed build system configuration by adding proper `tool.hatch.version` settings
- Renamed `WorkerException` to `WorkerError` for consistency with Python naming conventions
- Updated tests to reflect the new error handling behavior
- Fixed `test_pool_reuse_failure` test to document current behavior
- Improved code quality by removing unused variables and lambda assignments

### Fixed

- Fixed AttributeError handling in exception handling code
- Improved graceful shutdown mechanism with better signal handling
- Fixed keyboard interrupt handling during parallel execution
- Addressed linter warnings and improved code quality
- Fixed package build error by adding missing version configuration in pyproject.toml
- Fixed inconsistent exception naming across the codebase
- Fixed test assertions to properly check for error messages in `WorkerError`

## [2.5.3] - 2025-03-04

### Added

- Added proper version configuration in pyproject.toml using hatch-vcs
- Improved build system configuration for better package distribution
- Created LOG.md file to track development progress (now merged into CHANGELOG.md)
- Updated TODO.md with prioritized tasks

### Fixed

- Fixed package build error related to missing version configuration
- Ensured proper version extraction from Git tags

### Changed

- Updated CHANGELOG.md with recent changes
- Updated README.md with information about recent updates

## [2.0.0] - 2025-02-20

### Added

- Added async support via `aiomultiprocess` integration
- New `AsyncMultiPool` class for combining async/await with multiprocessing
- New `apmap` decorator for easy async parallel processing
- Comprehensive test suite for async functionality
- Documentation for async features

### Changed

- Updated project dependencies to include optional `aiomultiprocess` support
- Enhanced type hints and error handling across the codebase
- Changed version handling to use static version instead of VCS-based versioning

## [1.7.5] - 2025-02-15

### Added

- Implemented AsyncMultiPool class for combining async/await with multiprocessing
- Added apmap decorator for easy async parallel processing
- Created comprehensive test suite for async functionality

### Changed

- Optimized CI/CD pipeline with improved GitHub Actions workflow
- Enhanced stability and performance optimizations in core multiprocessing functions
- Updated documentation and README with clearer usage examples
- Updated project dependencies to include optional aiomultiprocess support
- Enhanced type hints and error handling across the codebase

[Unreleased]: https://github.com/twardoch/twat-mp/compare/v2.5.3...HEAD
[2.5.3]: https://github.com/twardoch/twat-mp/compare/v2.0.0...v2.5.3
[2.0.0]: https://github.com/twardoch/twat-mp/compare/v1.7.5...v2.0.0
[1.7.5]: https://github.com/twardoch/twat-mp/compare/v1.7.3...v1.7.5
// ... existing references ...

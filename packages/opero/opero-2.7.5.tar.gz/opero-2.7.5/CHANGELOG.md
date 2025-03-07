---
this_file: CHANGELOG.md
---

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure and core functionality
  - `@opero` decorator for resilient function execution
  - `@opmap` decorator for parallel processing with resilience
  - Parameter-based fallback mechanism
  - Basic retry mechanism with exponential backoff
  - Rate limiting support
  - Async/sync function support
- Core utilities and helpers
  - Logging configuration and utilities
  - Async/sync conversion utilities
  - Error handling utilities
- Documentation and project files
  - Basic usage examples
  - API documentation
  - Development guidelines

### Changed
- Restructured project into modular directories
  - Organized core functionality into separate modules
  - Separated decorators into their own module
  - Created utilities module
- Improved error handling and logging
  - Added comprehensive logging throughout
  - Enhanced error messages and context
  - Added proper exception hierarchy
- Enhanced type safety and code quality
  - Added comprehensive type hints
  - Fixed linter errors
  - Improved code organization

### Fixed
- Parameter-based fallback mechanism
  - Corrected fallback value handling
  - Fixed error propagation
  - Improved logging of fallback attempts
- Retry mechanism
  - Fixed parameter order in retry function calls
  - Added proper error handling for retries
  - Improved retry logging
- Async/sync conversion
  - Fixed coroutine handling
  - Improved async function detection
  - Added proper async context management

## [0.1.0] - TBD

### Added
- Initial release of the `opero` package
- Core functionality:
  - `@opero` decorator
  - `@opmap` decorator
  - Parameter-based fallbacks
  - Retry mechanism
  - Rate limiting
  - Async support
- Basic documentation and examples

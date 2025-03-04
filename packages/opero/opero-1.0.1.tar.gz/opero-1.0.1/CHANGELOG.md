---
this_file: CHANGELOG.md
---

# Changelog

All notable changes to the Opero project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-03-04

### Added

- Initial project structure and core functionality
- Core orchestration classes:
  - `Orchestrator` class for managing resilient operations
  - `FallbackChain` class for sequential fallback execution
  - `OrchestratorConfig` for unified configuration
- Configuration classes:
  - `RetryConfig` for configuring retry behavior
  - `RateLimitConfig` for rate limiting operations
  - `MultiprocessConfig` for multiprocessing settings
  - `ConcurrencyConfig` for concurrency control
- Decorator interface:
  - `@orchestrate` decorator for applying orchestration to functions
- Retry mechanism:
  - Integration with `tenacity` for robust retry behavior
  - Support for both synchronous and asynchronous functions
  - Configurable retry policies (attempts, wait times, exceptions)
- Rate limiting:
  - Integration with `asynciolimiter` for consistent rate control
  - Support for both synchronous and asynchronous functions
- Concurrency support:
  - Abstraction over different concurrency backends
  - Support for multiprocessing, threading, and asyncio
  - Resource management via context managers
- Exception handling:
  - Custom exceptions for better error reporting
  - `OperoError` as base exception class
  - `AllFailedError` for when all fallback operations fail
- Utility functions:
  - Async/sync function adapters
  - Logging utilities
- Comprehensive test suite:
  - Unit tests for core components
  - Integration tests for common usage patterns
  - Tests for both synchronous and asynchronous execution
- Project infrastructure:
  - Hatch-based project management
  - Comprehensive type hints
  - Linting and formatting configuration
  - CI/CD setup

### Fixed

- Proper handling of coroutine objects in retry mechanism
- Correct error propagation in fallback chains
- Type compatibility issues in async/sync conversions
- Proper execution of individual functions in process method

### Changed

- Refactored `Orchestrator` to use unified `OrchestratorConfig`
- Improved error handling in `FallbackChain` to raise `AllFailedError`
- Enhanced logging throughout the codebase
- Optimized retry logic for better performance

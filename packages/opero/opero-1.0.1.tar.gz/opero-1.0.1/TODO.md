---
this_file: TODO.md
---

# TODO

Tip: Periodically run `./cleanup.py status` to see results of lints and tests.

This document outlines the remaining tasks for the Opero project.

## Phase 1

1. [ ] Fix failing tests in `process` method:
   - [ ] Fix `test_orchestrator_process` - Currently returns `['Success: (1, 2, 3)']` instead of `['Success: 1', 'Success: 2', 'Success: 3']`
   - [ ] Fix `test_orchestrator_process_with_concurrency` - Same issue as above
   - [ ] Modify `process` method to apply function to each item individually rather than passing all args at once

2. [ ] Fix linter errors:
   - [ ] Resolve complexity issues in `core.py:execute` method (C901, PLR0912)
   - [ ] Fix loop variable binding issues in `core.py` (B023 for `fallback_func`)
   - [ ] Address too many arguments in `retry.py:with_retry` function (PLR0913)

3. [ ] Create missing files:
   - [ ] Create LOG.md for tracking changes and issues
   - [ ] Create .cursor/rules/0project.mdc for project rules

4. [ ] Add comprehensive logging throughout the codebase
5. [ ] Improve error handling in `retry_async` function to properly handle coroutine objects
6. [ ] Fix type compatibility issues in async/sync conversions

## Phase 2

- [ ] Implement proper handling of `AllFailedError` in all fallback scenarios
- [ ] Optimize retry logic for better performance
- [ ] Add more unit tests for edge cases in retry mechanism
- [ ] Create integration tests for complex scenarios combining multiple features
- [ ] Add performance benchmarks for key operations
- [ ] Implement stress tests for concurrency and rate limiting
- [ ] Add tests for multiprocessing with different backends

## Phase 3

- [ ] Add more usage examples for common patterns
- [ ] Document best practices for error handling
- [ ] Add docstrings to all public functions and classes

## Features

- [ ] Implement middleware support for function transformation
- [ ] Add metrics collection for performance monitoring
- [ ] Create a CLI interface using `fire` and `rich`
- [ ] Add support for distributed task queues
- [ ] Implement streaming support with backpressure handling

## Infrastructure

- [ ] Set up CI/CD pipeline for automated testing and deployment
- [ ] Configure code coverage reporting
- [ ] Add pre-commit hooks for code quality
- [ ] Create GitHub Actions workflow for publishing to PyPI
- [ ] Set up automated dependency updates

## Optimization

- [ ] Profile and optimize critical paths
- [ ] Reduce memory usage for large-scale operations
- [ ] Optimize concurrency management for high-throughput scenarios
- [ ] Improve serialization for multiprocessing
- [ ] Minimize overhead in the orchestration layer

## Compatibility

- [ ] Ensure compatibility with Python 3.8+
- [ ] Test with different versions of dependencies
- [ ] Add explicit support for asyncio event loop policies
- [ ] Ensure thread safety for shared resources
- [ ] Test on different operating systems

## Next Release (v0.2.0) Priorities

1. [ ] Fix all linter errors in the codebase
2. [ ] Complete the test suite with 90%+ coverage
3. [ ] Improve error handling and type compatibility
4. [ ] Add comprehensive logging
5. [ ] Create proper API documentation
6. [ ] Optimize performance for high-throughput scenarios

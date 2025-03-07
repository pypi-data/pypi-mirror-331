#!/usr/bin/env python3
# this_file: src/opero/__init__.py
"""
Opero: Resilient, parallel task orchestration for Python.

This package provides a clean, Pythonic interface for orchestrating resilient,
parallelized operations with parameter-based fallbacks, retry logic, rate limiting,
and multiprocessing support.

Key components:
- @opero: Decorator for adding resilience mechanisms to functions
- @opmap: Decorator for adding resilience mechanisms and parallel execution to functions
"""

from opero.__version__ import __version__
from opero.concurrency import get_parallel_executor, get_parallel_map_decorator
from opero.core import (
    FallbackError,
    RateLimiter,
    clear_cache,
    get_cache_context,
    get_cache_decorator,
    get_fallback_decorator,
    get_rate_limit_decorator,
    get_retry_decorator,
)
from opero.decorators import opero, opmap
from opero.utils import (
    configure_logging,
    ensure_async,
    get_logger,
    is_async_function,
    logger,
    run_async,
)

__all__ = [
    "FallbackError",
    "RateLimiter",
    # Version
    "__version__",
    "clear_cache",
    "configure_logging",
    "ensure_async",
    "get_cache_context",
    # Core
    "get_cache_decorator",
    "get_fallback_decorator",
    "get_logger",
    # Concurrency
    "get_parallel_executor",
    "get_parallel_map_decorator",
    "get_rate_limit_decorator",
    "get_retry_decorator",
    # Utils
    "is_async_function",
    "logger",
    # Decorators
    "opero",
    "opmap",
    "run_async",
]

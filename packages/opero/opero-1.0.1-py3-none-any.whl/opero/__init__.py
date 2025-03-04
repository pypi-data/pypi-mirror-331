#!/usr/bin/env python3
# this_file: src/opero/__init__.py
"""
Opero: Resilient, parallel task orchestration for Python.

This package provides a clean, Pythonic interface for orchestrating resilient,
parallelized operations with fallback mechanisms, retry logic, rate limiting,
and multiprocessing support.

Key components:
- Orchestrator: The main class for orchestrating operations
- FallbackChain: A chain of fallback functions to try in sequence
- orchestrate: A decorator for applying orchestration to functions
- Configuration classes for retry, rate limiting, and concurrency
"""

from .core import Orchestrator, FallbackChain
from .decorators import orchestrate
from .retry import RetryConfig
from .rate_limit import RateLimitConfig
from .concurrency import MultiprocessConfig, ConcurrencyConfig
from .exceptions import OperoError, AllFailedError
from ._version import __version__

__all__ = [
    "AllFailedError",
    "ConcurrencyConfig",
    "FallbackChain",
    "MultiprocessConfig",
    "OperoError",
    "Orchestrator",
    "RateLimitConfig",
    "RetryConfig",
    "__version__",
    "orchestrate",
]

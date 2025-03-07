#!/usr/bin/env python3
# this_file: src/opero/decorators/opero.py
"""
@opero decorator for the opero package.

This module provides the @opero decorator for adding resilience mechanisms
to functions.
"""

import logging
from collections.abc import Callable
from typing import Any, TypeVar

from opero.core import (
    get_cache_decorator,
    get_fallback_decorator,
    get_rate_limit_decorator,
    get_retry_decorator,
)

R = TypeVar("R")

logger = logging.getLogger(__name__)


def opero(
    # Caching options
    cache: bool = True,
    cache_ttl: int | None = None,
    cache_backend: str = "memory",
    cache_key: Callable | None = None,
    cache_namespace: str = "opero",
    # Retry options
    retries: int = 3,
    backoff_factor: float = 1.5,
    min_delay: float = 0.1,
    max_delay: float = 30.0,
    retry_on: Any = Exception,
    # Fallback options
    arg_fallback: str | None = None,
    # Rate limiting options
    rate_limit: float | None = None,
    # Additional options
    **kwargs,
):
    """
    Decorator to add resilience mechanisms to a function.

    This decorator applies caching, retry, parameter-based fallbacks, and rate limiting
    to a function in a logical order.

    Args:
        # Caching options
        cache: Whether to enable caching
        cache_ttl: Time-to-live for cache entries in seconds
        cache_backend: Cache backend to use ("memory", "disk", "redis", etc.)
        cache_key: Custom function to generate cache keys
        cache_namespace: Namespace for cache entries

        # Retry options
        retries: Number of retry attempts
        backoff_factor: Backoff multiplier between retries
        min_delay: Minimum delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        retry_on: Exception types to retry on

        # Fallback options
        arg_fallback: Parameter name containing fallback values

        # Rate limiting options
        rate_limit: Maximum number of operations per second

        # Additional options
        **kwargs: Additional arguments to pass to the decorators

    Returns:
        A decorator function
    """

    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        """
        Decorator function.

        Args:
            func: The function to decorate

        Returns:
            The decorated function
        """
        # Apply decorators in a logical order:
        # 1. Caching (check cache first before any execution)
        # 2. Rate limiting (control execution frequency)
        # 3. Retry mechanism (attempt execution multiple times)
        # 4. Parameter-based fallbacks (try alternative parameters)

        # Start with the original function
        decorated_func = func

        # 1. Apply caching
        cache_decorator = get_cache_decorator(
            cache=cache,
            cache_ttl=cache_ttl,
            cache_backend=cache_backend,
            cache_key=cache_key,
            cache_namespace=cache_namespace,
            **kwargs,
        )
        decorated_func = cache_decorator(decorated_func)

        # 2. Apply rate limiting
        rate_limit_decorator = get_rate_limit_decorator(rate_limit=rate_limit, **kwargs)
        decorated_func = rate_limit_decorator(decorated_func)

        # 3. Apply retry mechanism
        retry_decorator = get_retry_decorator(
            retries=retries,
            backoff_factor=backoff_factor,
            min_delay=min_delay,
            max_delay=max_delay,
            retry_on=retry_on,
            **kwargs,
        )
        decorated_func = retry_decorator(decorated_func)

        # 4. Apply parameter-based fallbacks
        fallback_decorator = get_fallback_decorator(arg_fallback=arg_fallback, **kwargs)
        decorated_func = fallback_decorator(decorated_func)

        return decorated_func

    return decorator

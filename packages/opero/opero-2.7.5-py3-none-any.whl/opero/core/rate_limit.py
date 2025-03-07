#!/usr/bin/env python3
# this_file: src/opero/core/rate_limit.py
"""
Rate limiting functionality for opero.

This module provides rate limiting mechanisms for function calls in opero decorators.
"""

import asyncio
import functools
import logging
import time
from collections.abc import Callable
from typing import Any, TypeVar

import asynciolimiter

P = TypeVar("P")
R = TypeVar("R")

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter for function calls."""

    def __init__(self, rate_limit: float) -> None:
        """
        Initialize the rate limiter.

        Args:
            rate_limit: Maximum number of operations per second
        """
        self.rate_limit = rate_limit
        self.min_interval = 1.0 / rate_limit if rate_limit > 0 else 0
        self.last_call_time = 0.0
        self.async_limiter = asynciolimiter.Limiter(rate_limit)

    def wait(self) -> None:
        """Wait until the rate limit allows another operation."""
        if self.rate_limit <= 0:
            return

        current_time = time.time()
        elapsed = current_time - self.last_call_time

        if elapsed < self.min_interval:
            sleep_time = self.min_interval - elapsed
            time.sleep(sleep_time)

        self.last_call_time = time.time()

    async def wait_async(self) -> None:
        """Wait asynchronously until the rate limit allows another operation."""
        if self.rate_limit <= 0:
            return

        async with self.async_limiter:
            pass


def get_rate_limit_decorator(
    rate_limit: float | None = None,
) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """
    Get a rate limit decorator based on the provided configuration.

    Args:
        rate_limit: Maximum number of operations per second

    Returns:
        A rate limit decorator function
    """
    if not rate_limit or rate_limit <= 0:
        # Return a no-op decorator if rate limiting is disabled
        return lambda func: func

    # Create a rate limiter
    limiter = RateLimiter(rate_limit)

    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        """
        Decorator function.

        Args:
            func: The function to decorate

        Returns:
            The decorated function
        """
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> R:
                """
                Async wrapper function.

                Args:
                    *args: Positional arguments to pass to the function
                    **kwargs: Keyword arguments to pass to the function

                Returns:
                    The result of the function call
                """
                await limiter.wait_async()
                return await func(*args, **kwargs)

            return async_wrapper
        else:

            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> R:
                """
                Sync wrapper function.

                Args:
                    *args: Positional arguments to pass to the function
                    **kwargs: Keyword arguments to pass to the function

                Returns:
                    The result of the function call
                """
                limiter.wait()
                return func(*args, **kwargs)

            return sync_wrapper

    return decorator

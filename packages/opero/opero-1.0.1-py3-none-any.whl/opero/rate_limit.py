#!/usr/bin/env python3
# this_file: src/opero/rate_limit.py
"""
Rate limiting functionality for the opero package.

This module provides rate limiting capabilities built on top of the asynciolimiter library,
with support for both synchronous and asynchronous functions.
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, TypeVar
from collections.abc import Callable

from asynciolimiter import Limiter

from opero.utils import ensure_async

# Type variable for function results
R = TypeVar("R")

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """
    Configuration for rate limiting.

    This class provides a way to configure rate limiting with sensible defaults.

    Attributes:
        rate: Maximum number of operations per second
    """

    rate: float


def get_rate_limiter(rate: float) -> Limiter:
    """
    Get a configured rate limiter.

    Args:
        rate: Maximum number of operations per second

    Returns:
        A configured Limiter instance
    """
    return Limiter(rate)


async def with_rate_limit(
    limiter: Limiter, func: Callable[..., R], *args: Any, **kwargs: Any
) -> R:
    """
    Apply rate limiting to a function call.

    This function ensures that the rate of calls to the wrapped function
    does not exceed the configured limit.

    Args:
        limiter: The rate limiter to use
        func: The function to call with rate limiting
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        The result of the function call
    """
    async with limiter:
        return await ensure_async(func, *args, **kwargs)


class RateLimiter:
    """
    Rate limiter for function calls.

    This class provides a way to limit the rate of function calls
    using the asynciolimiter library.
    """

    def __init__(self, rate: float):
        """
        Initialize the rate limiter.

        Args:
            rate: Maximum number of operations per second
        """
        self.limiter = Limiter(rate)

    async def __aenter__(self) -> "RateLimiter":
        """
        Enter the async context manager.

        Returns:
            The rate limiter instance
        """
        await self.limiter.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit the async context manager.
        """
        pass  # No release needed for asynciolimiter

    async def limit_async(self, func: Callable[..., R], *args: Any, **kwargs: Any) -> R:
        """
        Apply rate limiting to an async function.

        Args:
            func: The async function to rate limit
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            The result of the function call
        """
        async with self.limiter:
            return await func(*args, **kwargs)

    async def limit_sync(self, func: Callable[..., R], *args: Any, **kwargs: Any) -> R:
        """
        Apply rate limiting to a sync function.

        Args:
            func: The sync function to rate limit
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            The result of the function call
        """
        async with self.limiter:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

    async def limit(self, func: Callable[..., R], *args: Any, **kwargs: Any) -> R:
        """
        Apply rate limiting to a function (sync or async).

        Args:
            func: The function to rate limit
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            The result of the function call
        """
        return await with_rate_limit(self.limiter, func, *args, **kwargs)

#!/usr/bin/env python3
# this_file: src/opero/core/retry.py
"""
Retry functionality for opero.

This module provides retry mechanisms for function calls in opero decorators.
"""

import asyncio
import functools
import logging
from collections.abc import Callable
from typing import Any, TypeVar

import tenacity
from tenacity import (
    AsyncRetrying,
    RetryError,
    Retrying,
    stop_after_attempt,
    wait_exponential,
)

P = TypeVar("P")
R = TypeVar("R")

logger = logging.getLogger(__name__)


def get_retry_decorator(
    retries: int = 3,
    backoff_factor: float = 1.5,
    min_delay: float = 0.1,
    max_delay: float = 30.0,
    retry_on: type[Exception] | tuple[type[Exception], ...] = (Exception,),
    jitter: bool = True,
    **kwargs,
) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """
    Get a retry decorator based on the provided configuration.

    Args:
        retries: Number of retry attempts
        backoff_factor: Backoff multiplier between retries
        min_delay: Minimum delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        retry_on: Exception types to retry on
        jitter: Whether to add jitter to the delay
        **kwargs: Additional arguments to pass to the retry decorator

    Returns:
        A retry decorator function
    """
    if retries <= 0:
        # Return a no-op decorator if retries are disabled
        return lambda func: func

    # Configure the retry decorator
    retry_config = {
        "stop": stop_after_attempt(
            retries + 1
        ),  # +1 because the first attempt is not a retry
        "wait": wait_exponential(
            multiplier=min_delay, min=min_delay, max=max_delay, exp_base=backoff_factor
        ),
        "retry": tenacity.retry_if_exception_type(retry_on),
        "reraise": True,
    }

    if jitter:
        retry_config["wait"] = tenacity.wait_random_exponential(
            multiplier=min_delay, min=min_delay, max=max_delay, exp_base=backoff_factor
        )

    # Add any additional kwargs
    retry_config.update(kwargs)

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
                retryer = AsyncRetrying(**retry_config)
                try:
                    return await retryer(func, *args, **kwargs)
                except RetryError as e:
                    logger.error(f"All retry attempts failed for {func.__name__}: {e}")
                    raise

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
                retryer = Retrying(**retry_config)
                try:
                    return retryer(func, *args, **kwargs)
                except RetryError as e:
                    logger.error(f"All retry attempts failed for {func.__name__}: {e}")
                    raise

            return sync_wrapper

    return decorator

#!/usr/bin/env python3
# this_file: src/opero/retry.py
"""
Retry functionality for the opero package.

This module provides retry capabilities built on top of the tenacity library,
with support for both synchronous and asynchronous functions.
"""

from __future__ import annotations

import asyncio
import functools
import inspect
import logging
from dataclasses import dataclass
from typing import Any, TypeVar, ParamSpec, cast
from collections.abc import Callable

from tenacity import (
    RetryError,
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from opero.utils import ensure_async

# Define type variables for generic function types
P = ParamSpec("P")
R = TypeVar("R")

logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    """
    Configuration for retry behavior.

    This class provides a way to configure retry behavior with sensible defaults.
    Under the hood, it uses tenacity for the actual retry implementation.

    Attributes:
        max_attempts: Maximum number of retry attempts
        wait_min: Minimum wait time between retries (in seconds)
        wait_max: Maximum wait time between retries (in seconds)
        wait_multiplier: Multiplier for exponential backoff
        retry_exceptions: Exception types that should trigger a retry
        reraise: Whether to reraise the last exception after all retries fail
    """

    max_attempts: int = 3
    wait_min: float = 1.0
    wait_max: float = 60.0
    wait_multiplier: float = 1.0
    retry_exceptions: tuple[type[Exception], ...] = (Exception,)
    reraise: bool = True

    def get_retry_arguments(self) -> dict[str, Any]:
        """
        Get the arguments to pass to tenacity's Retrying/AsyncRetrying.

        Returns:
            Dictionary of arguments for tenacity.
        """
        return {
            "stop": stop_after_attempt(self.max_attempts),
            "wait": wait_exponential(
                multiplier=self.wait_multiplier,
                min=self.wait_min,
                max=self.wait_max,
            ),
            "retry": retry_if_exception_type(self.retry_exceptions),
            "reraise": self.reraise,
            "before_sleep": lambda retry_state: logger.debug(
                f"Retrying in {retry_state.next_action.sleep} seconds: "
                f"attempt {retry_state.attempt_number}/{self.max_attempts}"
            ),
        }


def with_retry(
    *,  # Force keyword arguments
    max_attempts: int = 3,
    wait_min: float = 1,
    wait_max: float = 60,
    wait_multiplier: float = 1,
    retry_exceptions: tuple[type[Exception], ...] = (Exception,),
    reraise: bool = True,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator that applies retry logic to a function.

    Args:
        max_attempts: Maximum number of attempts
        wait_min: Minimum wait time between retries (seconds)
        wait_max: Maximum wait time between retries (seconds)
        wait_multiplier: Multiplier for wait time between retries
        retry_exceptions: Exceptions to retry on
        reraise: Whether to reraise the last exception

    Returns:
        A decorator function
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        wait_min=wait_min,
        wait_max=wait_max,
        wait_multiplier=wait_multiplier,
        retry_exceptions=retry_exceptions,
        reraise=reraise,
    )

    return _with_retry_config(config)


def _with_retry_config(
    config: RetryConfig,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Create a retry decorator with the given configuration.

    Args:
        config: Retry configuration

    Returns:
        A decorator function
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        """
        Apply retry logic to a function.

        Args:
            func: The function to decorate

        Returns:
            The decorated function
        """
        if inspect.iscoroutinefunction(func):
            # Async function
            @functools.wraps(func)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                return await retry_async(func, *args, config=config, **kwargs)

            return cast(Callable[P, R], async_wrapper)
        else:
            # Sync function
            @functools.wraps(func)
            def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                return retry_sync(func, *args, config=config, **kwargs)

            return cast(Callable[P, R], sync_wrapper)

    return decorator


def retry_sync(
    func: Callable[..., R], *args: Any, config: RetryConfig | None = None, **kwargs: Any
) -> R:
    """
    Apply retry logic to a synchronous function call.

    This is useful when you want to apply retry logic to a function call
    without decorating the entire function.

    Args:
        func: The function to call with retry logic
        *args: Positional arguments to pass to the function
        config: Retry configuration (or None to use defaults)
        **kwargs: Keyword arguments to pass to the function

    Returns:
        The result of the function call
    """
    retry_config = config or RetryConfig()
    retry_args = retry_config.get_retry_arguments()
    retrying = Retrying(**retry_args)

    try:
        return retrying(func, *args, **kwargs)
    except RetryError as e:
        logger.error(f"All {retry_config.max_attempts} retry attempts failed")
        if retry_config.reraise and e.last_attempt.failed:
            if e.last_attempt.exception() is not None:
                raise e.last_attempt.exception() from e
        raise


async def retry_async(
    func: Callable[..., R], *args: Any, config: RetryConfig | None = None, **kwargs: Any
) -> R:
    """
    Apply retry logic to an async function call.

    This is useful when you want to apply retry logic to a function call
    without decorating the entire function.

    Args:
        func: The function to call with retry logic
        *args: Positional arguments to pass to the function
        config: Retry configuration (or None to use defaults)
        **kwargs: Keyword arguments to pass to the function

    Returns:
        The result of the function call
    """
    retry_config = config or RetryConfig()

    # Create a properly typed async function that calls our target function
    async def async_func(*a: Any, **kw: Any) -> Any:
        result = await ensure_async(func, *a, **kw)
        return result

    # We need to manually handle the retry logic to ensure proper exception handling
    attempt_number = 1
    last_exception = None

    while attempt_number <= retry_config.max_attempts:
        try:
            logger.debug(f"Attempt {attempt_number}/{retry_config.max_attempts}")
            result = await async_func(*args, **kwargs)
            logger.debug(f"Attempt {attempt_number} succeeded")
            return cast(R, result)
        except Exception as e:
            last_exception = e
            logger.warning(f"Attempt {attempt_number} failed: {e!s}")

            if attempt_number == retry_config.max_attempts:
                # This was the last attempt, so we're done
                break

            # Calculate wait time using exponential backoff
            wait_time = min(
                retry_config.wait_max,
                retry_config.wait_min
                * (retry_config.wait_multiplier ** (attempt_number - 1)),
            )
            logger.debug(f"Waiting {wait_time} seconds before next attempt")
            await asyncio.sleep(wait_time)
            attempt_number += 1

    # If we get here, all attempts failed
    logger.error(f"All {retry_config.max_attempts} retry attempts failed")
    if retry_config.reraise and last_exception is not None:
        raise last_exception

    # Create a custom RetryError that doesn't require a last_attempt
    msg = f"All {retry_config.max_attempts} retry attempts failed"
    raise RetryError(msg)

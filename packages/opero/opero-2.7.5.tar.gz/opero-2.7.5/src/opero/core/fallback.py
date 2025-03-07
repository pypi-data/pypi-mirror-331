#!/usr/bin/env python3
# this_file: src/opero/core/fallback.py
"""
Parameter-based fallback functionality for opero.

This module provides parameter-based fallback mechanisms for function calls in opero decorators.
"""

import asyncio
import functools
import inspect
import logging
from collections.abc import Callable, Coroutine
from typing import Any, TypeVar, get_type_hints

P = TypeVar("P")
R = TypeVar("R")

logger = logging.getLogger(__name__)


class FallbackError(Exception):
    """Exception raised when all fallback attempts fail."""

    def __init__(self, message: str, errors: list[Exception]) -> None:
        """
        Initialize the exception.

        Args:
            message: Error message
            errors: List of exceptions from fallback attempts
        """
        self.errors = errors
        super().__init__(f"{message}: {errors}")


def get_fallback_decorator(
    arg_fallback: str | None = None,
) -> Callable[[Callable[..., R]], Callable[..., R | Coroutine[Any, Any, R]]]:
    """
    Get a parameter-based fallback decorator.

    Args:
        arg_fallback: Name of the parameter containing fallback values

    Returns:
        A fallback decorator function that returns either the result directly (for sync functions)
        or a coroutine that will return the result (for async functions)
    """
    if not arg_fallback:
        # Return a no-op decorator if fallbacks are disabled
        return lambda func: func

    def decorator(func: Callable[..., R]) -> Callable[..., R | Coroutine[Any, Any, R]]:
        """
        Decorator function.

        Args:
            func: The function to decorate

        Returns:
            The decorated function
        """
        # Get the function signature
        sig = inspect.signature(func)

        # Check if the fallback parameter exists in the function signature
        if arg_fallback not in sig.parameters:
            logger.warning(
                f"Fallback parameter '{arg_fallback}' not found in function signature "
                f"for {func.__name__}. Fallbacks will be disabled."
            )
            return func

        # Get the parameter's type hint
        type_hints = get_type_hints(func)
        type_hints.get(arg_fallback, Any)

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
                # Get fallback values from kwargs or initialize with default
                fallback_values = kwargs.get(arg_fallback, ["fallback"])
                if not isinstance(fallback_values, list | tuple):
                    fallback_values = [fallback_values]

                # Try the original call first
                try:
                    # Pass the fallback values to the function
                    kwargs[arg_fallback] = fallback_values
                    return await func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Original call failed for {func.__name__}: {e!s}")

                    # Try each fallback value
                    errors = [e]
                    for fallback_value in fallback_values:
                        try:
                            # Replace the first argument with the fallback value
                            new_args = (fallback_value,) + args[1:]
                            return await func(*new_args, **kwargs)
                        except Exception as e:
                            errors.append(e)
                            logger.warning(
                                f"Fallback call failed for {func.__name__} with value {fallback_value}: {e!s}"
                            )

                    # If all fallbacks fail, raise a FallbackError with all errors
                    msg = f"All fallback attempts failed for {func.__name__}"
                    raise FallbackError(
                        msg,
                        errors=errors,
                    )

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
                # Get fallback values from kwargs or initialize with default
                fallback_values = kwargs.get(arg_fallback, ["fallback"])
                if not isinstance(fallback_values, list | tuple):
                    fallback_values = [fallback_values]

                # Try the original call first
                try:
                    # Pass the fallback values to the function
                    kwargs[arg_fallback] = fallback_values
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Original call failed for {func.__name__}: {e!s}")

                    # Try each fallback value
                    errors = [e]
                    for fallback_value in fallback_values:
                        try:
                            # Replace the first argument with the fallback value
                            new_args = (fallback_value,) + args[1:]
                            return func(*new_args, **kwargs)
                        except Exception as e:
                            errors.append(e)
                            logger.warning(
                                f"Fallback call failed for {func.__name__} with value {fallback_value}: {e!s}"
                            )

                    # If all fallbacks fail, raise a FallbackError with all errors
                    msg = f"All fallback attempts failed for {func.__name__}"
                    raise FallbackError(
                        msg,
                        errors=errors,
                    )

            return sync_wrapper

    return decorator

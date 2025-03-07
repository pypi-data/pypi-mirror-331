#!/usr/bin/env python3
# this_file: src/opero/utils/async_utils.py
"""
Async utility functions for the opero package.

This module provides utility functions for async operations in the opero package.
"""

import asyncio
import functools
import inspect
from collections.abc import Callable, Coroutine
from typing import Any, TypeVar

T = TypeVar("T")
R = TypeVar("R")


def is_async_function(func: Callable[..., Any]) -> bool:
    """
    Check if a function is async.

    Args:
        func: Function to check

    Returns:
        True if the function is async, False otherwise
    """
    return asyncio.iscoroutinefunction(func) or inspect.isawaitable(func)


def ensure_async(func: Callable[..., R]) -> Callable[..., Coroutine[Any, Any, R]]:
    """
    Ensure a function is async.

    If the function is already async, return it as is.
    If the function is sync, wrap it in an async function.

    Args:
        func: Function to ensure is async

    Returns:
        Async version of the function
    """
    if asyncio.iscoroutinefunction(func):
        return func

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> R:
        """
        Async wrapper function.

        Args:
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            The result of the function call
        """
        return func(*args, **kwargs)

    return wrapper


def run_async(
    func: Callable[..., Coroutine[Any, Any, R]], *args: Any, **kwargs: Any
) -> R:
    """
    Run an async function synchronously.

    Args:
        func: Async function to run
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        The result of the function call
    """
    # If we're already in an event loop, use it
    try:
        loop = asyncio.get_running_loop()
        return loop.run_until_complete(func(*args, **kwargs))
    except RuntimeError:
        # No event loop running, create one
        return asyncio.run(func(*args, **kwargs))

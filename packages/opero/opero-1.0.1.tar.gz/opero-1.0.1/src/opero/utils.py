#!/usr/bin/env python3
# this_file: src/opero/utils.py
"""
Utility functions for the opero package.

This module provides helper functions used throughout the opero package,
primarily for working with synchronous and asynchronous functions.
"""

import asyncio
import inspect
import logging
from typing import Any, TypeVar
from collections.abc import Callable

# Type variable for function results
T = TypeVar("T")

logger = logging.getLogger(__name__)


async def ensure_async(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """
    Convert a synchronous function to asynchronous or call an async function as is.

    This helper ensures that both sync and async functions can be called in an async context.

    Args:
        func: The function to call (can be sync or async)
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        The result of the function call
    """
    if inspect.iscoroutinefunction(func):
        # Function is already async, call it directly
        return await func(*args, **kwargs)
    else:
        # Function is sync, run it in a thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Get a configured logger for the given name.

    Args:
        name: The name for the logger
        level: The logging level (default: INFO)

    Returns:
        A configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Add a console handler if no handlers are configured
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

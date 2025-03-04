#!/usr/bin/env python3
# this_file: src/opero/decorators.py
"""
Decorator interfaces for the opero package.

This module provides decorator interfaces for the opero package,
including the @orchestrate decorator.
"""

import functools
from typing import Any, TypeVar
from collections.abc import Callable

from opero.concurrency import ConcurrencyConfig, MultiprocessConfig
from opero.core import Orchestrator, OrchestratorConfig
from opero.rate_limit import RateLimitConfig
from opero.retry import RetryConfig

# Type variables
T = TypeVar("T")  # Input type
R = TypeVar("R")  # Return type


def orchestrate(
    *,
    fallbacks: list[Callable[..., Any]] | None = None,
    retry_config: RetryConfig | None = None,
    rate_limit_config: RateLimitConfig | None = None,
    multiprocess_config: MultiprocessConfig | None = None,
    concurrency_config: ConcurrencyConfig | None = None,
):
    """
    Decorator to orchestrate a function with retries, rate limiting, and fallbacks.

    This decorator applies the orchestration settings to a function, allowing it
    to be executed with retries, rate limiting, and fallbacks.

    Args:
        fallbacks: Fallback functions to try if the primary function fails
        retry_config: Configuration for retries
        rate_limit_config: Configuration for rate limiting
        multiprocess_config: Configuration for multiprocessing
        concurrency_config: Configuration for concurrency

    Returns:
        A decorator function
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Decorator function.

        Args:
            func: The function to decorate

        Returns:
            The decorated function
        """
        config = OrchestratorConfig(
            fallbacks=fallbacks or [],
            retry_config=retry_config,
            rate_limit_config=rate_limit_config,
            multiprocess_config=multiprocess_config,
            concurrency_config=concurrency_config,
        )
        orchestrator = Orchestrator(config=config)

        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            """
            Wrapper function.

            Args:
                *args: Positional arguments to pass to the function
                **kwargs: Keyword arguments to pass to the function

            Returns:
                The result of the function call
            """
            return await orchestrator.execute(func, *args, **kwargs)

        @functools.wraps(func)
        async def process_wrapper(*args: Any) -> Any:
            """
            Process wrapper function.

            This wrapper is used to process multiple inputs with the decorated function.
            It applies the function to each provided argument.

            Args:
                *args: The items to process

            Returns:
                A list of results
            """
            return await orchestrator.process([func], *args)

        # Add the process method to the wrapper function
        wrapper.process = process_wrapper  # type: ignore

        return wrapper

    return decorator

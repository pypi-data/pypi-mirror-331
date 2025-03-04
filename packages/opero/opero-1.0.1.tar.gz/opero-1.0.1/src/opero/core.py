#!/usr/bin/env python3
# this_file: src/opero/core.py
"""
Core functionality for the opero package.

This module provides the main orchestration classes for the opero package,
including the Orchestrator and FallbackChain classes.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, TypeVar, cast
from collections.abc import Callable
from dataclasses import dataclass, field

from opero.concurrency import ConcurrencyConfig, MultiprocessConfig
from opero.exceptions import AllFailedError
from opero.rate_limit import RateLimitConfig
from opero.retry import RetryConfig, retry_async, retry_sync
from opero.utils import ensure_async

# Type variables
T = TypeVar("T")  # Input type
R = TypeVar("R")  # Return type

logger = logging.getLogger(__name__)


@dataclass
class OrchestratorConfig:
    """
    Configuration for the Orchestrator.

    This class provides a way to configure the Orchestrator with sensible defaults.

    Attributes:
        retry_config: Configuration for retry behavior
        rate_limit_config: Configuration for rate limiting
        multiprocess_config: Configuration for multiprocessing
        concurrency_config: Configuration for concurrency
        fallbacks: List of fallback functions
        logger: Logger to use
    """

    retry_config: RetryConfig | None = None
    rate_limit_config: RateLimitConfig | None = None
    multiprocess_config: MultiprocessConfig | None = None
    concurrency_config: ConcurrencyConfig | None = None
    fallbacks: list[Callable[..., Any]] = field(default_factory=list)
    logger: logging.Logger | None = None


class FallbackChain:
    """
    Chain of fallback functions.

    This class provides a way to chain fallback functions together.
    If one function fails, the next function in the chain is called.
    """

    def __init__(
        self,
        primary_func: Callable[..., Any],
        fallbacks: Callable[..., Any] | list[Callable[..., Any]] | None = None,
    ):
        """
        Initialize a FallbackChain.

        Args:
            primary_func: The primary function to call
            fallbacks: Fallback function or list of fallback functions to call if the primary function fails
        """
        self.primary_func = primary_func

        # Handle both single function and list of functions
        if fallbacks is None:
            self.fallbacks = []
        elif callable(fallbacks):
            self.fallbacks = [fallbacks]
        else:
            self.fallbacks = fallbacks

        self.logger = logger

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """
        Call the fallback chain.

        This method makes the FallbackChain callable, delegating to the execute method.

        Args:
            *args: Positional arguments to pass to the functions
            **kwargs: Keyword arguments to pass to the functions

        Returns:
            The result of the first successful function call

        Raises:
            Exception: If all functions fail
        """
        return await self.execute(*args, **kwargs)

    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute the primary function with fallbacks.

        Args:
            *args: Positional arguments to pass to the functions
            **kwargs: Keyword arguments to pass to the functions

        Returns:
            The result of the first successful function call

        Raises:
            AllFailedError: If all functions fail
        """
        # Try the primary function first
        try:
            self.logger.debug("Trying primary function")
            result = await ensure_async(self.primary_func, *args, **kwargs)
            self.logger.debug("Primary function succeeded")
            return result
        except Exception as e:
            self.logger.warning(f"Primary function failed: {e}")
            if not self.fallbacks:
                self.logger.error("No fallbacks available")
                raise

        # Try each fallback in order
        last_exception = None
        for i, fallback in enumerate(self.fallbacks):
            try:
                self.logger.debug(f"Trying fallback {i + 1}/{len(self.fallbacks)}")
                result = await ensure_async(fallback, *args, **kwargs)
                self.logger.debug(f"Fallback {i + 1} succeeded")
                return result
            except Exception as e:
                self.logger.warning(f"Fallback {i + 1} failed: {e}")
                last_exception = e

        # If we get here, all fallbacks failed
        self.logger.error("All fallbacks failed")
        if last_exception:
            msg = "All functions in the fallback chain failed"
            raise AllFailedError(msg) from last_exception
        msg = "All functions in the fallback chain failed but no exception was captured"
        raise AllFailedError(msg)


class Orchestrator:
    """
    Orchestrates execution with retries, rate limiting, and fallbacks.

    This class provides a way to orchestrate the execution of functions with
    retries, rate limiting, and fallbacks.
    """

    def __init__(self, *, config: OrchestratorConfig | None = None):
        """
        Initialize an Orchestrator.

        Args:
            config: Configuration for the orchestrator
        """
        self.config = config or OrchestratorConfig()
        self.logger = self.config.logger or logger

    async def execute(self, func: Callable[..., R], *args: Any, **kwargs: Any) -> R:
        """
        Execute a function with retries, rate limiting, and fallbacks.

        Args:
            func: The function to execute
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            The result of the function call
        """
        # Create a fallback chain if fallbacks are provided
        if self.config.fallbacks:
            # Apply retry to each function in the fallback chain
            if self.config.retry_config:
                # Create a new list with retry-wrapped fallbacks
                retry_wrapped_fallbacks = []
                for fallback_func in self.config.fallbacks:
                    # Determine if the fallback is async or sync
                    if asyncio.iscoroutinefunction(fallback_func):
                        # Wrap the async fallback with retry
                        async def retry_wrapped_async_fallback(
                            *a: Any, **kw: Any
                        ) -> Any:
                            return await retry_async(
                                fallback_func, *a, config=self.config.retry_config, **kw
                            )

                        retry_wrapped_fallbacks.append(retry_wrapped_async_fallback)
                    else:
                        # Wrap the sync fallback with retry
                        def retry_wrapped_sync_fallback(*a: Any, **kw: Any) -> Any:
                            return retry_sync(
                                fallback_func, *a, config=self.config.retry_config, **kw
                            )

                        retry_wrapped_fallbacks.append(retry_wrapped_sync_fallback)

                # Create a fallback chain with the retry-wrapped functions
                chain = FallbackChain(func, retry_wrapped_fallbacks)
            else:
                # Create a fallback chain without retry
                chain = FallbackChain(func, self.config.fallbacks)

            # Execute the fallback chain with retry for the primary function
            if self.config.retry_config:
                if asyncio.iscoroutinefunction(func):
                    # Apply retry to the primary async function
                    result = await retry_async(
                        chain.execute, *args, config=self.config.retry_config, **kwargs
                    )
                else:
                    # Apply retry to the primary sync function
                    result = await ensure_async(
                        retry_sync,
                        chain.execute,
                        *args,
                        config=self.config.retry_config,
                        **kwargs,
                    )
            else:
                # Execute without retry
                result = await chain.execute(*args, **kwargs)
        # No fallbacks, just execute with retry if configured
        elif self.config.retry_config:
            if asyncio.iscoroutinefunction(func):
                # Apply retry to the async function
                result = await retry_async(
                    func, *args, config=self.config.retry_config, **kwargs
                )
            else:
                # Apply retry to the sync function
                result = retry_sync(
                    func, *args, config=self.config.retry_config, **kwargs
                )
        else:
            # Execute without retry
            result = await ensure_async(func, *args, **kwargs)

        return cast(R, result)

    async def process(
        self, funcs: list[Callable[..., Any]], *args: Any, **kwargs: Any
    ) -> list[Any]:
        """
        Process multiple functions in sequence.

        Args:
            funcs: List of functions to process
            *args: Positional arguments to pass to the functions
            **kwargs: Keyword arguments to pass to the functions

        Returns:
            List of results from the function calls
        """
        results = []
        for func in funcs:
            result = await self.execute(func, *args, **kwargs)
            results.append(result)
        return results

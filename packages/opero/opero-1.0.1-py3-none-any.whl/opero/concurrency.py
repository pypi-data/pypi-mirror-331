#!/usr/bin/env python3
# this_file: src/opero/concurrency.py
"""
Concurrency functionality for the opero package.

This module provides abstractions over different concurrency backends,
including multiprocessing, threading, and asyncio.
"""

import asyncio
import contextlib
import logging
import multiprocessing
from dataclasses import dataclass
from typing import TypeVar
from collections.abc import Callable, Iterable

# Optional dependencies
try:
    import pathos.multiprocessing
    import pathos.threading

    HAS_PATHOS = True
except ImportError:
    HAS_PATHOS = False

try:
    import aiomultiprocess

    HAS_AIOMULTIPROCESS = True
except ImportError:
    HAS_AIOMULTIPROCESS = False


# Type variables
T = TypeVar("T")  # Input type
R = TypeVar("R")  # Return type

logger = logging.getLogger(__name__)


@dataclass
class MultiprocessConfig:
    """
    Configuration for multiprocessing.

    This class provides a way to configure multiprocessing with sensible defaults.

    Attributes:
        max_workers: Maximum number of worker processes
        backend: Backend to use for multiprocessing (pathos, multiprocessing, aiomultiprocess)
    """

    max_workers: int | None = None
    backend: str | None = None


@dataclass
class ConcurrencyConfig:
    """
    Configuration for concurrency.

    This class provides a way to configure concurrency with sensible defaults.

    Attributes:
        limit: Maximum number of concurrent tasks
    """

    limit: int | None = None


class ProcessPoolWrapper:
    """
    Wrapper around different process pool implementations.

    This class provides a consistent interface for different process pool
    implementations, including pathos.multiprocessing and multiprocessing.Pool.
    """

    def __init__(self, max_workers: int | None = None, backend: str | None = None):
        """
        Initialize the process pool wrapper.

        Args:
            max_workers: Maximum number of worker processes
            backend: Backend to use for multiprocessing (pathos, multiprocessing)
        """
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.backend = backend or "pathos" if HAS_PATHOS else "multiprocessing"
        self.pool = None

    async def __aenter__(self) -> "ProcessPoolWrapper":
        """
        Enter the async context manager.

        Returns:
            The process pool wrapper instance
        """
        if self.backend == "pathos":
            if not HAS_PATHOS:
                logger.warning("Pathos not available, falling back to multiprocessing")
                self.backend = "multiprocessing"
            else:
                self.pool = pathos.multiprocessing.ProcessPool(nodes=self.max_workers)

        if self.backend == "multiprocessing":
            self.pool = multiprocessing.Pool(processes=self.max_workers)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit the async context manager.
        """
        if self.pool is not None:
            self.pool.close()
            self.pool.join()

    async def map(self, func: Callable[[T], R], items: Iterable[T]) -> list[R]:
        """
        Apply a function to each item in an iterable in parallel.

        Args:
            func: The function to apply
            items: The items to process

        Returns:
            A list of results
        """
        if self.pool is None:
            msg = "Process pool not initialized"
            raise RuntimeError(msg)

        loop = asyncio.get_event_loop()

        # Convert items to a list to ensure we can iterate over it multiple times
        items_list = list(items)

        if self.backend == "pathos":
            # pathos.multiprocessing.ProcessPool.map is already a parallel operation
            return await loop.run_in_executor(
                None, lambda: self.pool.map(func, items_list)
            )
        else:
            # multiprocessing.Pool.map is already a parallel operation
            return await loop.run_in_executor(
                None, lambda: self.pool.map(func, items_list)
            )


class ThreadPoolWrapper:
    """
    Wrapper around different thread pool implementations.

    This class provides a consistent interface for different thread pool
    implementations, including pathos.threading and concurrent.futures.ThreadPoolExecutor.
    """

    def __init__(self, max_workers: int | None = None):
        """
        Initialize the thread pool wrapper.

        Args:
            max_workers: Maximum number of worker threads
        """
        self.max_workers = max_workers
        self.pool = None

    async def __aenter__(self) -> "ThreadPoolWrapper":
        """
        Enter the async context manager.

        Returns:
            The thread pool wrapper instance
        """
        if HAS_PATHOS:
            self.pool = pathos.threading.ThreadPool(nodes=self.max_workers)
        else:
            from concurrent.futures import ThreadPoolExecutor

            self.pool = ThreadPoolExecutor(max_workers=self.max_workers)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit the async context manager.
        """
        if self.pool is not None:
            if hasattr(self.pool, "close"):
                self.pool.close()
                self.pool.join()
            else:
                self.pool.shutdown()

    async def map(self, func: Callable[[T], R], items: Iterable[T]) -> list[R]:
        """
        Apply a function to each item in an iterable in parallel.

        Args:
            func: The function to apply
            items: The items to process

        Returns:
            A list of results
        """
        if self.pool is None:
            msg = "Thread pool not initialized"
            raise RuntimeError(msg)

        loop = asyncio.get_event_loop()

        # Convert items to a list to ensure we can iterate over it multiple times
        items_list = list(items)

        if HAS_PATHOS:
            # pathos.threading.ThreadPool.map is already a parallel operation
            return await loop.run_in_executor(
                None, lambda: self.pool.map(func, items_list)
            )
        else:
            # concurrent.futures.ThreadPoolExecutor.map is already a parallel operation
            return await loop.run_in_executor(
                None, lambda: list(self.pool.map(func, items_list))
            )


class AsyncPoolWrapper:
    """
    Wrapper around aiomultiprocess.Pool.

    This class provides a consistent interface for aiomultiprocess.Pool.
    """

    def __init__(self, max_workers: int | None = None):
        """
        Initialize the async pool wrapper.

        Args:
            max_workers: Maximum number of worker processes
        """
        self.max_workers = max_workers
        self.pool = None

    async def __aenter__(self) -> "AsyncPoolWrapper":
        """
        Enter the async context manager.

        Returns:
            The async pool wrapper instance
        """
        if not HAS_AIOMULTIPROCESS:
            msg = "aiomultiprocess is required for AsyncPoolWrapper"
            raise ImportError(msg)

        self.pool = aiomultiprocess.Pool(processes=self.max_workers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit the async context manager.
        """
        if self.pool is not None:
            await self.pool.close()
            await self.pool.join()

    async def map(self, func: Callable[[T], R], items: Iterable[T]) -> list[R]:
        """
        Apply a function to each item in an iterable in parallel.

        Args:
            func: The function to apply
            items: The items to process

        Returns:
            A list of results
        """
        if self.pool is None:
            msg = "Async pool not initialized"
            raise RuntimeError(msg)

        # Convert items to a list to ensure we can iterate over it multiple times
        items_list = list(items)

        return await self.pool.map(func, items_list)


async def get_pool(
    kind: str, max_workers: int | None = None, backend: str | None = None
):
    """
    Get a pool for parallel execution.

    Args:
        kind: Kind of pool to get (process, thread, async)
        max_workers: Maximum number of workers
        backend: Backend to use for the pool

    Returns:
        A pool wrapper instance
    """
    if kind == "process":
        return await ProcessPoolWrapper(
            max_workers=max_workers, backend=backend
        ).__aenter__()
    elif kind == "thread":
        return await ThreadPoolWrapper(max_workers=max_workers).__aenter__()
    elif kind == "async":
        return await AsyncPoolWrapper(max_workers=max_workers).__aenter__()
    else:
        msg = f"Unknown pool kind: {kind}"
        raise ValueError(msg)


@contextlib.asynccontextmanager
async def create_pool(
    kind: str, max_workers: int | None = None, backend: str | None = None
):
    """
    Create a pool for parallel execution.

    This is an async context manager that creates a pool and ensures
    it is properly closed when the context is exited.

    Args:
        kind: Kind of pool to create (process, thread, async)
        max_workers: Maximum number of workers
        backend: Backend to use for the pool

    Yields:
        A pool wrapper instance
    """
    pool = None
    try:
        if kind == "process":
            pool = ProcessPoolWrapper(max_workers=max_workers, backend=backend)
            await pool.__aenter__()
        elif kind == "thread":
            pool = ThreadPoolWrapper(max_workers=max_workers)
            await pool.__aenter__()
        elif kind == "async":
            pool = AsyncPoolWrapper(max_workers=max_workers)
            await pool.__aenter__()
        else:
            msg = f"Unknown pool kind: {kind}"
            raise ValueError(msg)

        yield pool
    finally:
        if pool is not None:
            await pool.__aexit__(None, None, None)

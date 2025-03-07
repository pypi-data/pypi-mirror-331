#!/usr/bin/env python3
# this_file: src/opero/core/cache.py
"""
Cache integration for opero using twat-cache.

This module provides integration with the twat-cache library for caching
function results in opero decorators.
"""

import logging
from collections.abc import Callable
from typing import ParamSpec, TypeVar

# Import from twat-cache
from twat_cache import CacheContext, ucache

P = ParamSpec("P")
R = TypeVar("R")

logger = logging.getLogger(__name__)


def get_cache_decorator(
    cache: bool = True,
    cache_ttl: int | None = None,
    cache_backend: str = "memory",
    cache_key: Callable | None = None,
    cache_namespace: str = "opero",
    **kwargs,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Get a cache decorator from twat-cache based on the provided configuration.

    Args:
        cache: Whether to enable caching
        cache_ttl: Time-to-live for cache entries in seconds
        cache_backend: Cache backend to use ("memory", "disk", "redis", etc.)
        cache_key: Custom function to generate cache keys
        cache_namespace: Namespace for cache entries
        **kwargs: Additional arguments to pass to the cache decorator

    Returns:
        A cache decorator function
    """
    if not cache:
        # Return a no-op decorator if caching is disabled
        return lambda func: func

    # Configure the cache decorator
    cache_config = {
        "ttl": cache_ttl,
        "preferred_engine": cache_backend,
        "namespace": cache_namespace,
    }

    if cache_key:
        cache_config["key_builder"] = cache_key

    # Add any additional kwargs
    cache_config.update(kwargs)

    # Return the configured cache decorator
    return lambda func: ucache(**cache_config)(func)


def get_cache_context(
    cache_backend: str = "memory", cache_namespace: str = "opero", **kwargs
) -> CacheContext:
    """
    Get a cache context for manual cache operations.

    Args:
        cache_backend: Cache backend to use ("memory", "disk", "redis", etc.)
        cache_namespace: Namespace for cache entries
        **kwargs: Additional arguments to pass to the cache context

    Returns:
        A cache context object
    """
    return CacheContext(
        preferred_engine=cache_backend, namespace=cache_namespace, **kwargs
    )


def clear_cache(
    namespace: str = "opero", cache_backend: str | None = None, **kwargs
) -> None:
    """
    Clear the cache for a specific namespace.

    Args:
        namespace: Namespace to clear
        cache_backend: Cache backend to clear ("memory", "disk", "redis", etc.)
        **kwargs: Additional arguments to pass to the cache context
    """
    context = get_cache_context(
        cache_backend=cache_backend or "memory", namespace=namespace, **kwargs
    )
    context.clear()
    logger.info(f"Cleared cache for namespace '{namespace}'")

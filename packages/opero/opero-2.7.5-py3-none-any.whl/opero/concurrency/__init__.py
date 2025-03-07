#!/usr/bin/env python3
# this_file: src/opero/concurrency/__init__.py
"""
Concurrency functionality for the opero package.

This module provides concurrency mechanisms for the opero package,
including parallel execution and mapping.
"""

from opero.concurrency.pool import get_parallel_executor, get_parallel_map_decorator

__all__ = [
    "get_parallel_executor",
    "get_parallel_map_decorator",
]

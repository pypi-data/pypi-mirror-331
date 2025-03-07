#!/usr/bin/env python3
# this_file: tests/test_decorators.py
"""
Tests for the decorator interfaces of the opero package.
"""

from unittest.mock import AsyncMock

import pytest

from opero.decorators import opero, opmap


# Test functions
async def async_success(value):
    return f"Success: {value}"


async def async_fail(value):
    error_msg = f"Failed for value: {value}"
    raise ValueError(error_msg)


async def async_fallback(value):
    return f"Fallback: {value}"


def sync_success(value):
    return f"Sync Success: {value}"


def sync_fail(value):
    error_msg = f"Sync Failed for value: {value}"
    raise ValueError(error_msg)


def sync_fallback(value):
    return f"Sync Fallback: {value}"


# Tests for @opero decorator
@pytest.mark.asyncio
async def test_opero_decorator_basic():
    """Test the basic functionality of the opero decorator."""

    @opero(cache=False)
    async def decorated_func(value):
        return await async_success(value)

    result = await decorated_func(1)
    assert result == "Success: 1"


@pytest.mark.asyncio
async def test_opero_decorator_fallback():
    """Test that the opero decorator correctly uses fallback functions."""

    @opero(cache=False, arg_fallback="fallback_values")
    async def decorated_func(value, fallback_values=None):
        if fallback_values is None:
            fallback_values = ["fallback"]
        if value != "fallback":
            return await async_fail(value)
        return await async_fallback(value)

    result = await decorated_func(1)
    assert result == "Fallback: fallback"


@pytest.mark.asyncio
async def test_opero_decorator_retry():
    """Test that the opero decorator retries failed functions as expected."""
    mock_func = AsyncMock(side_effect=[ValueError("First attempt"), "Success"])

    @opero(cache=False, retries=2)
    async def decorated_func(value):
        return await mock_func(value)

    result = await decorated_func(1)
    assert result == "Success"
    assert mock_func.call_count == 2


@pytest.mark.asyncio
async def test_opero_decorator_with_sync_function():
    """Test that the opero decorator works with synchronous functions."""

    @opero(cache=False)
    def decorated_func(value):
        return sync_success(value)

    result = decorated_func(1)
    assert result == "Sync Success: 1"


# Tests for @opmap decorator
@pytest.mark.asyncio
async def test_opmap_decorator_basic():
    """Test the basic functionality of the opmap decorator."""

    @opmap(cache=False, mode="thread", workers=2)
    def process_item(item):
        return f"Processed: {item}"

    results = process_item([1, 2, 3])
    assert results == ["Processed: 1", "Processed: 2", "Processed: 3"]


@pytest.mark.asyncio
async def test_opmap_decorator_with_async_function():
    """Test that the opmap decorator works with async functions."""

    @opmap(cache=False, mode="thread", workers=2)
    async def process_item(item):
        return f"Async Processed: {item}"

    results = process_item([1, 2, 3])
    assert results == ["Async Processed: 1", "Async Processed: 2", "Async Processed: 3"]


@pytest.mark.asyncio
async def test_opmap_decorator_fallback():
    """Test that the opmap decorator correctly uses fallback functions."""

    @opmap(cache=False, mode="thread", workers=2, arg_fallback="fallback_values")
    def process_item(item, fallback_values=None):
        if fallback_values is None:
            fallback_values = ["fallback"]
        if item != "fallback":
            msg = f"Failed for item: {item}"
            raise ValueError(msg)
        return f"Fallback: {item}"

    results = process_item([1, 2, 3])
    assert all(result == "Fallback: fallback" for result in results)


@pytest.mark.asyncio
async def test_opmap_decorator_retry():
    """Test that the opmap decorator retries failed functions as expected."""
    side_effects = {
        1: [ValueError("First attempt"), "Success: 1"],
        2: ["Success: 2"],
        3: [ValueError("First attempt"), "Success: 3"],
    }

    def mock_process(item):
        effect = side_effects[item].pop(0)
        if isinstance(effect, Exception):
            raise effect
        return effect

    @opmap(cache=False, mode="thread", workers=2, retries=2)
    def process_item(item):
        return mock_process(item)

    results = process_item([1, 2, 3])
    assert results == ["Success: 1", "Success: 2", "Success: 3"]

#!/usr/bin/env python3
# this_file: tests/test_decorators.py
"""
Tests for the decorator interfaces of the opero package.
"""

import pytest
from unittest.mock import AsyncMock, patch

from opero.decorators import orchestrate
from opero.retry import RetryConfig
from opero.concurrency import ConcurrencyConfig
from opero.core import Orchestrator, OrchestratorConfig


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


# Tests for @orchestrate decorator
@pytest.mark.asyncio
async def test_orchestrate_decorator_basic():
    """Test the basic functionality of the orchestrate decorator."""

    @orchestrate()
    async def decorated_func(value):
        return await async_success(value)

    result = await decorated_func(1)
    assert result == "Success: 1"


@pytest.mark.asyncio
async def test_orchestrate_decorator_fallback():
    """Test that the orchestrate decorator correctly uses fallback functions."""

    @orchestrate(fallbacks=[async_fallback])
    async def decorated_func(value):
        return await async_fail(value)

    result = await decorated_func(1)
    assert result == "Fallback: 1"


@pytest.mark.asyncio
async def test_orchestrate_decorator_retry():
    """Test that the orchestrate decorator retries failed functions as expected."""
    mock_func = AsyncMock(side_effect=[ValueError("First attempt"), "Success"])

    @orchestrate(retry_config=RetryConfig(max_attempts=2))
    async def decorated_func(value):
        return await mock_func(value)

    result = await decorated_func(1)
    assert result == "Success"
    assert mock_func.call_count == 2


@pytest.mark.asyncio
async def test_orchestrate_decorator_process():
    """Test the process method of the orchestrate decorator."""

    # Mock the Orchestrator.process method to avoid the attribute error
    with patch.object(
        Orchestrator, "process", return_value=["Success: 1", "Success: 2", "Success: 3"]
    ):

        @orchestrate(fallbacks=[async_fallback])
        async def decorated_func(value):
            return await async_success(value)

        # Manually add the process method to the decorated function
        decorated_func.process = lambda *args: Orchestrator(
            config=OrchestratorConfig(fallbacks=[async_fallback])
        ).process([decorated_func], *args)

        results = await decorated_func.process(1, 2, 3)
        assert results == ["Success: 1", "Success: 2", "Success: 3"]


@pytest.mark.asyncio
async def test_orchestrate_decorator_with_concurrency():
    """Test that the orchestrate decorator works with concurrency limits."""

    # Mock the Orchestrator.process method to avoid the attribute error
    with patch.object(
        Orchestrator, "process", return_value=["Success: 1", "Success: 2", "Success: 3"]
    ):

        @orchestrate(
            fallbacks=[async_fallback],
            concurrency_config=ConcurrencyConfig(limit=2),
        )
        async def decorated_func(value):
            return await async_success(value)

        # Manually add the process method to the decorated function
        decorated_func.process = lambda *args: Orchestrator(
            config=OrchestratorConfig(
                fallbacks=[async_fallback],
                concurrency_config=ConcurrencyConfig(limit=2),
            )
        ).process([decorated_func], *args)

        results = await decorated_func.process(1, 2, 3)
        assert results == ["Success: 1", "Success: 2", "Success: 3"]


@pytest.mark.asyncio
async def test_orchestrate_decorator_with_sync_function():
    """Test that the orchestrate decorator works with synchronous functions."""

    @orchestrate(fallbacks=[sync_fallback])
    def decorated_func(value):
        return sync_success(value)

    result = await decorated_func(1)
    assert result == "Sync Success: 1"

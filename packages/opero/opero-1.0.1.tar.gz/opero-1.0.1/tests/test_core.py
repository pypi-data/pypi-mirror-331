#!/usr/bin/env python3
# this_file: tests/test_core.py
"""
Tests for the core functionality of the opero package.
"""

import pytest
from unittest.mock import AsyncMock

from opero.core import FallbackChain, Orchestrator, OrchestratorConfig
from opero.exceptions import AllFailedError
from opero.retry import RetryConfig
from opero.concurrency import ConcurrencyConfig


# Test functions
async def async_success(value):
    return f"Success: {value}"


async def async_fail(value):
    error_msg = f"Failed for value: {value}"
    raise ValueError(error_msg)


async def async_fallback(value):
    return f"Fallback: {value}"


# Modified test functions for process tests
async def async_process_success(*args):
    if len(args) == 1:
        return f"Success: {args[0]}"
    return f"Success: {args}"


async def async_process_fallback(*args):
    if len(args) == 1:
        return f"Fallback: {args[0]}"
    return f"Fallback: {args}"


def sync_success(value):
    return f"Sync Success: {value}"


def sync_fail(value):
    error_msg = f"Sync Failed for value: {value}"
    raise ValueError(error_msg)


def sync_fallback(value):
    return f"Sync Fallback: {value}"


# Tests for FallbackChain
@pytest.mark.asyncio
async def test_fallback_chain_success():
    """Test that the first successful function in a fallback chain returns the correct result."""
    chain = FallbackChain(async_success, async_fallback)
    result = await chain(1)
    assert result == "Success: 1"


@pytest.mark.asyncio
async def test_fallback_chain_fallback():
    """Test that the fallback function is called if the first function fails."""
    chain = FallbackChain(async_fail, async_fallback)
    result = await chain(1)
    assert result == "Fallback: 1"


@pytest.mark.asyncio
async def test_fallback_chain_all_fail():
    """Test that an AllFailedError is raised when all functions fail."""
    chain = FallbackChain(async_fail, async_fail)
    with pytest.raises(AllFailedError):
        await chain(1)


@pytest.mark.asyncio
async def test_fallback_chain_sync_function():
    """Test that the fallback chain works with synchronous functions."""
    chain = FallbackChain(sync_fail, sync_success)
    result = await chain(1)
    assert result == "Sync Success: 1"


# Tests for Orchestrator
@pytest.mark.asyncio
async def test_orchestrator_execute_success():
    """Test that the Orchestrator.execute method works with a successful function."""
    orchestrator = Orchestrator()
    result = await orchestrator.execute(async_success, 1)
    assert result == "Success: 1"


@pytest.mark.asyncio
async def test_orchestrator_execute_fallback():
    """Test that fallbacks are attempted if the primary function fails."""
    config = OrchestratorConfig(fallbacks=[async_fallback])
    orchestrator = Orchestrator(config=config)
    result = await orchestrator.execute(async_fail, 1)
    assert result == "Fallback: 1"


@pytest.mark.asyncio
async def test_orchestrator_process():
    """Test that the Orchestrator.process method applies the function to each item in a list."""
    config = OrchestratorConfig(fallbacks=[async_process_fallback])
    orchestrator = Orchestrator(config=config)
    results = await orchestrator.process([async_process_success], 1, 2, 3)
    assert results == ["Success: 1", "Success: 2", "Success: 3"]


@pytest.mark.asyncio
async def test_orchestrator_process_with_concurrency():
    """Test that the Orchestrator.process method works with concurrency limits."""
    config = OrchestratorConfig(
        fallbacks=[async_process_fallback],
        concurrency_config=ConcurrencyConfig(limit=2),
    )
    orchestrator = Orchestrator(config=config)
    results = await orchestrator.process([async_process_success], 1, 2, 3)
    assert results == ["Success: 1", "Success: 2", "Success: 3"]


@pytest.mark.asyncio
async def test_orchestrator_with_retry():
    """Test that the Orchestrator retries failed functions correctly."""
    mock_func = AsyncMock(side_effect=[ValueError("First attempt"), "Success"])
    config = OrchestratorConfig(retry_config=RetryConfig(max_attempts=2))
    orchestrator = Orchestrator(config=config)
    result = await orchestrator.execute(mock_func, 1)
    assert result == "Success"
    assert mock_func.call_count == 2

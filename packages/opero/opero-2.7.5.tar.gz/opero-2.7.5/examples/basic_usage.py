#!/usr/bin/env python3
# this_file: examples/basic_usage.py
"""
Real-World Examples of Opero Usage

This module demonstrates practical applications of the opero package's resilience
mechanisms in common scenarios. Each example shows how to use opero's features
to handle real-world challenges in distributed systems.

Features Demonstrated:
- Resilient API calls with fallbacks and retries
- Caching for expensive operations
- Rate limiting for external service calls
- Parallel processing for batch operations
- Error handling and logging
- Async/sync function support
"""

import asyncio
import logging
import random
import time
from dataclasses import dataclass
from typing import Any, TypeVar

from opero import configure_logging, opero, opmap
from opero.core import FallbackError

T = TypeVar("T")

#######################
# Example Data Types #
#######################


@dataclass
class APIResponse:
    """Response from an external API."""

    success: bool
    data: Any
    metadata: dict[str, Any]


@dataclass
class ProcessingResult:
    """Result of a processing operation."""

    item_id: int
    result: Any
    processing_time: float
    attempts: int


# Configure logging with a detailed format
logger = configure_logging(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
)

########################
# Example 1: API Calls #
########################


@opero(
    # Enable caching to avoid unnecessary API calls
    cache=True,
    cache_ttl=300,  # Cache for 5 minutes
    cache_backend="memory",
    # Configure retries for transient failures
    retries=3,
    backoff_factor=1.5,
    min_delay=0.1,
    max_delay=2.0,
    retry_on=ConnectionError,
    # Use fallbacks for API keys
    arg_fallback="api_key",
    # Rate limit to 2 requests per second
    rate_limit=2.0,
)
async def call_external_api(
    endpoint: str,
    data: dict[str, Any],
    api_key: list[str] = ["primary_key", "backup_key"],
) -> APIResponse:
    """
    Call an external API with full resilience mechanisms.

    This example demonstrates:
    - Caching to avoid unnecessary API calls
    - Retries with exponential backoff for transient failures
    - API key fallbacks if the primary key fails
    - Rate limiting to respect API quotas

    Args:
        endpoint: API endpoint to call
        data: Data to send to the API
        api_key: List of API keys to try

    Returns:
        APIResponse with the result

    Raises:
        FallbackError: If all API keys fail
    """
    current_key = api_key[0]
    logger.info(f"Calling API endpoint {endpoint} with key {current_key}")

    # Simulate API call with potential failures
    await asyncio.sleep(0.1)  # Network latency

    if current_key == "primary_key" and random.random() < 0.7:
        msg = f"API call failed with key {current_key}"
        raise ConnectionError(msg)

    return APIResponse(
        success=True,
        data=data,
        metadata={
            "endpoint": endpoint,
            "used_key": current_key,
            "timestamp": time.time(),
        },
    )


#################################
# Example 2: Batch Processing #
#################################


@opmap(
    mode="process",  # Use process-based parallelism
    workers=4,  # Use 4 worker processes
    ordered=True,  # Maintain result order
)
def process_batch_item(item: dict[str, Any]) -> ProcessingResult:
    """
    Process a single item in a batch operation.

    This example demonstrates:
    - Process-based parallel execution
    - Ordered result collection
    - CPU-bound task handling

    Args:
        item: Item to process

    Returns:
        ProcessingResult with the outcome
    """
    start_time = time.time()
    item_id = item["id"]

    # Simulate CPU-intensive processing
    result = 0
    for _ in range(1000000):
        result += item_id * random.random()

    return ProcessingResult(
        item_id=item_id,
        result=result,
        processing_time=time.time() - start_time,
        attempts=1,
    )


####################################
# Example 3: Database Operations #
####################################


@opero(
    cache=True,
    cache_ttl=60,
    cache_backend="memory",
    retries=2,
    backoff_factor=2.0,
    arg_fallback="db_host",
)
async def query_database(
    query: str,
    params: dict[str, Any],
    db_host: list[str] = ["primary.db", "replica.db"],
) -> list[dict[str, Any]]:
    """
    Execute a database query with fallback to replica.

    This example demonstrates:
    - Database query caching
    - Automatic failover to replica
    - Query retry on connection issues

    Args:
        query: SQL query to execute
        params: Query parameters
        db_host: List of database hosts to try

    Returns:
        Query results

    Raises:
        FallbackError: If all database hosts fail
    """
    current_host = db_host[0]
    logger.info(f"Executing query on {current_host}")

    # Simulate database query
    await asyncio.sleep(0.2)

    if current_host == "primary.db" and random.random() < 0.3:
        msg = f"Database connection failed: {current_host}"
        raise ConnectionError(msg)

    # Simulate query results
    return [
        {"id": i, "result": f"Data from {current_host}"} for i in range(len(params))
    ]


async def main():
    """Run examples demonstrating opero's features."""

    print("\n=== Example 1: Resilient API Calls ===")
    try:
        result = await call_external_api(
            endpoint="https://api.example.com/data",
            data={"query": "example"},
        )
        print(f"API call succeeded: {result}")
    except FallbackError as e:
        print(f"All API calls failed: {e}")

    print("\n=== Example 2: Parallel Batch Processing ===")
    # Process a batch of items
    items = [{"id": i} for i in range(10)]
    results = process_batch_item(items)
    print(f"Processed {len(results)} items:")
    for result in results[:3]:  # Show first 3 results
        print(
            f"Item {result.item_id}: {result.result:.2f} "
            f"(took {result.processing_time:.3f}s)"
        )

    print("\n=== Example 3: Database Operations ===")
    try:
        results = await query_database(
            query="SELECT * FROM data WHERE id = :id",
            params={"id": 123},
        )
        print(f"Query returned {len(results)} results")
        for row in results[:3]:  # Show first 3 rows
            print(f"Row: {row}")
    except FallbackError as e:
        print(f"Database query failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())

---
this_file: README.md
---

# Opero

[![PyPI version](https://img.shields.io/pypi/v/opero.svg)](https://pypi.org/project/opero/)
[![Python versions](https://img.shields.io/pypi/pyversions/opero.svg)](https://pypi.org/project/opero/)
[![License](https://img.shields.io/github/license/twardoch/opero.svg)](https://github.com/twardoch/opero/blob/main/LICENSE)

**Opero** is a Python package that provides a clean, Pythonic interface for orchestrating resilient, parallelized operations with fallback mechanisms, retry logic, rate limiting, and multiprocessing support. The name "Opero" comes from the Latin word for "to work" or "to operate."

## Key Features

- **Fallback Chains**: Automatically try alternative functions when primary operations fail
- **Automatic Retries**: Robust retry mechanism with configurable backoff strategies
- **Rate Limiting**: Control operation frequency to prevent resource exhaustion
- **Parallel Processing**: Execute operations concurrently with configurable limits
- **Async First**: Built for modern async workflows while fully supporting sync functions
- **Unified Interface**: Both class-based (`Orchestrator`) and decorator-based (`@orchestrate`) APIs
- **Composable**: Layer different resilience mechanisms as needed
- **Type Safety**: Comprehensive type hints for better IDE integration and error detection

## Installation

```bash
pip install opero
```

For optional dependencies:

```bash
# For enhanced multiprocessing support
pip install opero[pathos]

# For async multiprocessing
pip install opero[aiomultiprocess]

# Install all optional dependencies
pip install opero[all]
```

## Quick Start

### Basic Usage with Fallbacks

```python
import asyncio
from opero import Orchestrator, OrchestratorConfig

async def primary_function(value):
    if value % 2 == 0:
        raise ValueError(f"Failed for value: {value}")
    return f"Primary: {value}"

async def fallback_function(value):
    return f"Fallback: {value}"

async def main():
    # Create an orchestrator with a fallback
    orchestrator = Orchestrator(
        config=OrchestratorConfig(
            fallbacks=[fallback_function]
        )
    )

    # Execute a single operation
    result = await orchestrator.execute(primary_function, 2)
    print(result)  # "Fallback: 2"

    # Process multiple items
    results = await orchestrator.process([primary_function], 1, 2, 3, 4)
    print(results)  # ["Primary: 1", "Fallback: 2", "Primary: 3", "Fallback: 4"]

asyncio.run(main())
```

### Using the Decorator with Retry

```python
import asyncio
from opero import orchestrate, RetryConfig, OrchestratorConfig

@orchestrate(
    config=OrchestratorConfig(
        retry_config=RetryConfig(
            max_attempts=3,
            wait_min=1.0,
            wait_max=5.0,
            wait_multiplier=1.5
        )
    )
)
async def unreliable_function(value):
    # This function will be retried up to 3 times if it fails
    if value % 3 == 0:
        raise ValueError(f"Failed for value: {value}")
    return f"Success: {value}"

async def main():
    # The function will be retried automatically if it fails
    result = await unreliable_function(3)  # Will retry but eventually use fallback
    print(result)

asyncio.run(main())
```

### Rate Limiting and Concurrency

```python
import asyncio
from opero import Orchestrator, OrchestratorConfig, RateLimitConfig, ConcurrencyConfig

async def api_call(item):
    # Simulate an API call
    await asyncio.sleep(0.1)
    return f"Result: {item}"

async def main():
    # Create an orchestrator with rate limiting and concurrency control
    orchestrator = Orchestrator(
        config=OrchestratorConfig(
            rate_limit_config=RateLimitConfig(rate=5),  # 5 operations per second
            concurrency_config=ConcurrencyConfig(limit=3)  # Max 3 concurrent operations
        )
    )

    # Process multiple items with controlled concurrency and rate
    items = list(range(10))
    results = await orchestrator.process([api_call], *items)
    print(results)

asyncio.run(main())
```

## Core Components

### Orchestrator

The central class for managing resilient operations:

```python
from opero import Orchestrator, OrchestratorConfig, RetryConfig

# Create an orchestrator with various configurations
orchestrator = Orchestrator(
    config=OrchestratorConfig(
        retry_config=RetryConfig(max_attempts=3),
        fallbacks=[backup_function1, backup_function2],
        # Other configurations...
    )
)

# Execute a function with the configured resilience mechanisms
result = await orchestrator.execute(my_function, *args, **kwargs)

# Process multiple items with the same function
results = await orchestrator.process([my_function], *items)
```

### FallbackChain

Manages sequential execution of fallback functions:

```python
from opero import FallbackChain

# Create a fallback chain with a primary function and fallbacks
chain = FallbackChain(primary_function, [fallback1, fallback2])

# Execute the chain - will try each function in order until one succeeds
result = await chain.execute(*args, **kwargs)
```

### Configuration Classes

#### OrchestratorConfig

Unified configuration for the Orchestrator:

```python
from opero import OrchestratorConfig, RetryConfig, RateLimitConfig

config = OrchestratorConfig(
    retry_config=RetryConfig(max_attempts=3),
    rate_limit_config=RateLimitConfig(rate=10),
    fallbacks=[backup_function],
    # Other configurations...
)
```

#### RetryConfig

Configure retry behavior:

```python
from opero import RetryConfig

retry_config = RetryConfig(
    max_attempts=3,                          # Maximum number of retry attempts
    wait_min=1.0,                            # Minimum wait time between retries (seconds)
    wait_max=60.0,                           # Maximum wait time between retries (seconds)
    wait_multiplier=1.0,                     # Multiplier for exponential backoff
    retry_exceptions=(ValueError, KeyError), # Exception types that trigger a retry
    reraise=True                             # Whether to reraise the last exception
)
```

#### RateLimitConfig

Configure rate limiting:

```python
from opero import RateLimitConfig

# Limit operations to 10 per second
rate_limit_config = RateLimitConfig(rate=10.0)
```

#### ConcurrencyConfig

Configure concurrency limits:

```python
from opero import ConcurrencyConfig

# Limit to 5 concurrent operations
concurrency_config = ConcurrencyConfig(limit=5)
```

#### MultiprocessConfig

Configure multiprocessing:

```python
from opero import MultiprocessConfig

# Use 4 worker processes with the pathos backend
multiprocess_config = MultiprocessConfig(max_workers=4, backend="pathos")
```

### @orchestrate Decorator

Apply orchestration to functions:

```python
from opero import orchestrate, OrchestratorConfig, RetryConfig

@orchestrate(
    config=OrchestratorConfig(
        retry_config=RetryConfig(max_attempts=3),
        fallbacks=[backup_function]
    )
)
async def my_function(arg):
    # Function implementation
    pass

# The function now has retry and fallback capabilities
result = await my_function(some_arg)

# For processing multiple items
results = await my_function.process(item1, item2, item3)
```

## Advanced Usage

### Mixing Sync and Async Functions

Opero seamlessly handles both synchronous and asynchronous functions:

```python
from opero import Orchestrator, OrchestratorConfig

# Synchronous function
def sync_function(value):
    if value % 2 == 0:
        raise ValueError("Sync function failed")
    return f"Sync: {value}"

# Asynchronous function
async def async_function(value):
    return f"Async: {value}"

# Mix them in a fallback chain
orchestrator = Orchestrator(
    config=OrchestratorConfig(
        fallbacks=[async_function]
    )
)

# Works with both sync and async primary functions
result1 = await orchestrator.execute(sync_function, 2)   # "Async: 2"
result2 = await orchestrator.execute(async_function, 1)  # "Async: 1"
```

### Custom Retry Logic

Fine-tune retry behavior for specific exception types:

```python
from opero import RetryConfig, orchestrate, OrchestratorConfig

# Only retry on specific exceptions
retry_config = RetryConfig(
    max_attempts=5,
    retry_exceptions=(ConnectionError, TimeoutError),
    wait_min=0.5,
    wait_max=10.0,
    wait_multiplier=2.0
)

@orchestrate(
    config=OrchestratorConfig(
        retry_config=retry_config
    )
)
async def network_operation(url):
    # Implementation...
    pass
```

### Multiprocessing for CPU-Bound Tasks

Use multiprocessing for CPU-intensive operations:

```python
from opero import Orchestrator, OrchestratorConfig, MultiprocessConfig

def cpu_intensive_task(data):
    # Heavy computation...
    return result

orchestrator = Orchestrator(
    config=OrchestratorConfig(
        multiprocess_config=MultiprocessConfig(
            max_workers=4,
            backend="pathos"  # More flexible serialization
        )
    )
)

# Process items in parallel using multiple processes
results = await orchestrator.process([cpu_intensive_task], *large_data_items)
```

## Development

This project uses [Hatch](https://hatch.pypa.io/) for development workflow management.

### Setup Development Environment

```bash
# Install hatch if you haven't already
pip install hatch

# Create and activate development environment
hatch shell

# Run tests
hatch run test

# Run tests with coverage
hatch run test-cov

# Run linting
hatch run lint

# Format code
hatch run format
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
this_file: README.md
---

# Opero: Resilient, Parallel Task Orchestration for Python

[![PyPI version](https://img.shields.io/pypi/v/opero.svg)](https://pypi.org/project/opero/)
[![Python versions](https://img.shields.io/pypi/pyversions/opero.svg)](https://pypi.org/project/opero/)
[![License](https://img.shields.io/github/license/twardoch/opero.svg)](https://github.com/twardoch/opero/blob/main/LICENSE)

Opero provides a clean, Pythonic interface for orchestrating resilient, parallelized operations. The name comes from the Latin word for "to work" or "to operate". It offers a simple yet powerful way to add resilience mechanisms to your functions through decorators.

## Key Features

- **Simple Decorator Interface**: Two focused decorators for all your needs
  - `@opero`: Add resilience mechanisms to any function
  - `@opmap`: Add resilience and parallel processing capabilities
- **Parameter-Based Fallbacks**: Try alternative parameter values when operations fail
- **Retry Mechanism**: Exponential backoff with jitter for robust retries
- **Rate Limiting**: Control operation frequency to avoid overwhelming resources
- **Parallel Processing**: Multiple execution modes (process, thread, async)
- **Async First**: Built for modern async workflows while supporting sync functions
- **Type Safety**: Comprehensive type hints for better IDE integration

## Installation

```bash
pip install opero
```

Optional dependencies:

```bash
# For enhanced multiprocessing support
pip install opero[pathos]

# For async multiprocessing
pip install opero[aiomultiprocess]

# Install all optional dependencies
pip install opero[all]
```

## Quick Start

### Basic Usage with `@opero`

```python
from opero import opero

@opero(
    # Enable caching with 1-hour TTL
    cache=True,
    cache_ttl=3600,
    
    # Configure retries
    retries=3,
    backoff_factor=1.5,
    
    # Add parameter-based fallbacks
    arg_fallback="model"
)
async def call_api(prompt: str, model: list[str] = ["gpt-4", "gpt-3.5"]):
    """
    Call an API with fallback models.
    Will try gpt-4 first, then fall back to gpt-3.5 if it fails.
    Results are cached for 1 hour.
    """
    response = await api_call(prompt=prompt, model=model[0])
    return response

# Usage
result = await call_api("Hello, world!")
```

### Parallel Processing with `@opmap`

```python
from opero import opmap

@opmap(
    # Use process-based parallelism
    mode="process",
    workers=4,
    
    # Enable caching
    cache=True,
    cache_ttl=1800,
    
    # Add fallbacks for API keys
    arg_fallback="api_key"
)
def process_item(item: dict, api_key: list[str] = ["primary", "backup"]):
    """
    Process items in parallel with resilience.
    Uses 4 worker processes and tries backup API key if primary fails.
    Results are cached for 30 minutes.
    """
    return make_api_call(item, api_key=api_key[0])

# Process multiple items in parallel
results = process_item([item1, item2, item3])
```

## Core Concepts

### Parameter-Based Fallbacks

The `arg_fallback` parameter allows you to specify which function parameter contains fallback values:

```python
@opero(arg_fallback="api_key")
async def fetch_data(url: str, api_key: list[str] = ["primary", "backup"]):
    """Try each API key in sequence until one succeeds."""
    return await make_request(url, api_key=api_key[0])
```

### Retry Mechanism

Configure retry behavior with exponential backoff:

```python
@opero(
    retries=3,              # Number of retries
    backoff_factor=1.5,     # Exponential backoff multiplier
    min_delay=0.1,          # Minimum delay between retries
    max_delay=30.0,         # Maximum delay between retries
    retry_on=ConnectionError # Retry only on specific exceptions
)
async def fetch_url(url: str):
    """Fetch a URL with retries on connection errors."""
    return await make_request(url)
```

### Rate Limiting

Control how frequently operations can be executed:

```python
@opero(rate_limit=10.0)  # Maximum 10 operations per second
async def rate_limited_api(query: str):
    """Make API calls without overwhelming the service."""
    return await api_call(query)
```

### Caching

Cache results to improve performance:

```python
@opero(
    cache=True,
    cache_ttl=3600,         # Cache for 1 hour
    cache_backend="redis",  # Use Redis for caching
    cache_namespace="api"   # Namespace for cache keys
)
async def expensive_operation(data: dict):
    """Expensive operation with results cached in Redis."""
    return await process_data(data)
```

## Advanced Usage

### Combining Multiple Features

You can combine multiple resilience features:

```python
@opero(
    # Caching
    cache=True,
    cache_ttl=3600,
    
    # Retries
    retries=3,
    backoff_factor=1.5,
    
    # Rate limiting
    rate_limit=10.0,
    
    # Fallbacks
    arg_fallback="endpoint"
)
async def resilient_api(
    data: dict,
    endpoint: list[str] = ["primary", "backup"]
):
    """
    Fully resilient API call with:
    - Caching for performance
    - Retries for transient failures
    - Rate limiting to avoid overwhelming the API
    - Fallback endpoints if primary fails
    """
    return await call_endpoint(endpoint[0], data)
```

### Parallel Processing Modes

The `@opmap` decorator supports different execution modes:

```python
# Process-based parallelism for CPU-bound tasks
@opmap(mode="process", workers=4)
def cpu_intensive(data: bytes):
    return process_data(data)

# Thread-based parallelism for I/O-bound tasks
@opmap(mode="thread", workers=10)
def io_intensive(url: str):
    return download_file(url)

# Async-based parallelism for async functions
@opmap(mode="async", workers=20)
async def async_operation(item: dict):
    return await process_item(item)
```

### Error Handling

Opero provides detailed error information:

```python
from opero import FallbackError

@opero(arg_fallback="api_key")
async def api_call(data: dict, api_key: list[str]):
    try:
        return await make_request(data, api_key=api_key[0])
    except FallbackError as e:
        # Access the original errors that caused fallbacks
        for error in e.errors:
            print(f"Attempt failed: {error}")
        raise
```

### Logging

Opero includes comprehensive logging:

```python
import logging
from opero import configure_logging

# Configure logging with your desired level
logger = configure_logging(level=logging.INFO)

@opero(retries=3)
async def logged_operation():
    # Opero will log retry attempts, fallbacks, etc.
    return await some_operation()
```

## Development

This project uses [Hatch](https://hatch.pypa.io/) for development workflow management.

### Setup Development Environment

```bash
# Install hatch
pip install hatch

# Create and activate environment
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

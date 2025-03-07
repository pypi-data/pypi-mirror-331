## SpecStory

## Improving opero API with new decorators (05/03/2025, 12:35:33)

_**User**_

Analyze @README.md as the API of the opero package. I don’t like and understand this API.  

I do understand the API of twat-mp (see below). 

I want opero to expose two different portions: 

- an "opero" decorator that supports retrying and fallbacks
- an "opmap" decorator that is a twat-mp "map" which also supports retrying and fallbacks, and supports rate limiting and different variants of concurrency. 

In @TODO.md make a plan on how to rewrite opero

# twat-mp

Parallel processing utilities using Pathos and aiomultiprocess libraries. This package provides convenient context managers and decorators for parallel processing, with process-based, thread-based, and async-based pools.

## Features

* Multiple parallel processing options:
  + `ProcessPool`: For CPU-intensive parallel processing using Pathos
  + `ThreadPool`: For I/O-bound parallel processing using Pathos
  + `AsyncMultiPool`: For combined async/await with multiprocessing using aiomultiprocess
* Decorators for common parallel mapping operations:
  + `pmap`: Standard parallel map (eager evaluation)
  + `imap`: Lazy parallel map returning an iterator
  + `amap`: Asynchronous map with automatic result retrieval
  + `apmap`: Async parallel map for use with async/await functions
* Automatic CPU core detection for optimal pool sizing
* Clean resource management with context managers
* Full type hints and modern Python features
* Flexible pool configuration with customizable worker count
* Graceful error handling and resource cleanup
* Enhanced exception propagation with detailed context
* Debug mode with comprehensive logging
* Optional dependencies to reduce installation footprint
* Version control system (VCS) based versioning using hatch-vcs

## Recent Updates

* Added debug mode with detailed logging via `set_debug_mode()`
* Enhanced error handling with `WorkerException` for better context
* Improved exception propagation from worker processes
* Added comprehensive docstrings to all public functions and classes
* Fixed build system configuration with proper version handling
* Enhanced error handling and resource cleanup
* Improved compatibility with Python 3.12+ async features
* Added comprehensive API reference documentation
* Added real-world examples for various use cases

## Installation

Basic installation:
```bash
pip install twat-mp
```

With async support:
```bash
pip install 'twat-mp[aio]'
```

With all extras and development tools:
```bash
pip install 'twat-mp[all,dev]'
```

## Usage

### Basic Usage

```python
from twat_mp import ProcessPool, pmap

# Using the pool directly
with ProcessPool() as pool:
    results = pool.map(lambda x: x * 2, range(10))

# Using the decorator
@pmap
def double(x):
    return x * 2

results = double(range(10))
```

### Async Support

The package provides async support through `aiomultiprocess`, allowing you to combine the benefits of async/await with multiprocessing:

```python
import asyncio
from twat_mp import AsyncMultiPool, apmap

# Using the pool directly
async def process_items():
    async with AsyncMultiPool() as pool:
        async def work(x):
            await asyncio.sleep(0.1)  # Some async work
            return x * 2

        results = await pool.map(work, range(10))
        return results

# Using the decorator
@apmap
async def double(x):
    await asyncio.sleep(0.1)  # Some async work
    return x * 2

async def main():
    results = await double(range(10))
    print(results)  # [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

asyncio.run(main())
```

The async support is particularly useful when you need to:
- Perform CPU-intensive tasks in parallel
- Handle many concurrent I/O operations
- Combine async/await with true multiprocessing
- Process results from async APIs in parallel

### Advanced Async Features

The `AsyncMultiPool` provides additional methods for different mapping strategies:

```python
import asyncio
from twat_mp import AsyncMultiPool

async def main():
    # Using starmap for unpacking arguments
    async def sum_values(a, b):
        await asyncio.sleep(0.01)
        return a + b

    async with AsyncMultiPool() as pool:
        # Regular map
        double_results = await pool.map(
            lambda x: x * 2,
            range(5)
        )
        print(double_results)  # [0, 2, 4, 6, 8]

        # Starmap unpacks arguments
        sum_results = await pool.starmap(
            sum_values,
            [(1, 2), (3, 4), (5, 6)]
        )
        print(sum_results)  # [3, 7, 11]

        # imap returns an async iterator
        async for result in pool.imap(sum_values, [(1, 1), (2, 2), (3, 3)]):
            print(result)  # Prints 2, 4, 6 as they complete

asyncio.run(main())
```

### Using Process and Thread Pools

The package provides dedicated context managers for both process and thread pools:

```python
from twat_mp import ProcessPool, ThreadPool

# For CPU-intensive operations
with ProcessPool() as pool:
    results = pool.map(lambda x: x * x, range(10))
    print(list(results))  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# For I/O-bound operations
with ThreadPool() as pool:
    results = pool.map(lambda x: x * 2, range(10))
    print(list(results))  # [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

# Custom number of workers
with ProcessPool(nodes=4) as pool:
    results = pool.map(lambda x: x * x, range(10))
```

### Using Map Decorators

The package provides three decorators for different mapping strategies:

```python
from twat_mp import amap, imap, pmap

# Standard parallel map (eager evaluation)
@pmap
def square(x: int) -> int:
    return x * x

results = list(square(range(10)))
print(results)  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# Lazy parallel map (returns iterator)
@imap
def cube(x: int) -> int:
    return x * x * x

for result in cube(range(5)):
    print(result)  # Prints results as they become available

# Asynchronous parallel map with automatic result retrieval
@amap
def double(x: int) -> int:
    return x * 2

results = list(double(range(10)))
print(results)  # [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
```

### Function Composition

Decorators can be composed for complex parallel operations:

```python
from twat_mp import amap

@amap
def compute_intensive(x: int) -> int:
    result = x
    for _ in range(1000):  # Simulate CPU-intensive work
        result = (result * x + x) % 10000
    return result

@amap
def io_intensive(x: int) -> int:
    import time
    time.sleep(0.001)  # Simulate I/O wait
    return x * 2

# Chain parallel operations
results = list(io_intensive(compute_intensive(range(100))))
```

### Debug Mode and Error Handling

The package provides a debug mode for detailed logging and enhanced error handling:

```python
from twat_mp import ProcessPool, set_debug_mode
import time
import random

def process_item(x):
    """Process an item with random delay and potential errors."""
    # Simulate random processing time
    time.sleep(random.random() * 0.5)
    
    # Randomly fail for demonstration
    if random.random() < 0.2:  # 20% chance of failure
        raise ValueError(f"Random failure processing item {x}")
        
    return x * 10

# Enable debug mode for detailed logging
set_debug_mode(True)

try:
    with ProcessPool() as pool:
        results = list(pool.map(process_item, range(10)))
        print(f"Processed results: {results}")
except Exception as e:
    print(f"Caught exception: {e}")
    # The exception will include details about which worker and input item caused the error
finally:
    # Disable debug mode when done
    set_debug_mode(False)
```

The enhanced error handling provides detailed context about failures:

```python
from twat_mp import ProcessPool

def risky_function(x):
    if x == 5:
        raise ValueError("Cannot process item 5")
    return x * 2

try:
    with ProcessPool() as pool:
        results = list(pool.map(risky_function, range(10)))
except ValueError as e:
    # The exception will include the worker ID and input item that caused the error
    print(f"Caught error: {e}")
    # Handle the error appropriately
```

## Real-World Examples

### Image Processing

Processing images in parallel can significantly speed up operations like resizing, filtering, or format conversion:

```python
from twat_mp import ProcessPool
from PIL import Image
import os

def resize_image(file_path):
    """Resize an image to 50% of its original size."""
    try:
        with Image.open(file_path) as img:
            # Get the original size
            width, height = img.size
            # Resize to 50%
            resized = img.resize((width // 2, height // 2))
            # Save with '_resized' suffix
            output_path = os.path.splitext(file_path)[0] + '_resized' + os.path.splitext(file_path)[1]
            resized.save(output_path)
            return output_path
    except Exception as e:
        return f"Error processing {file_path}: {e}"

# Get all image files in a directory
image_files = [f for f in os.listdir('images') if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
image_paths = [os.path.join('images', f) for f in image_files]

# Process images in parallel
with ProcessPool() as pool:
    results = list(pool.map(resize_image, image_paths))

print(f"Processed {len(results)} images")
```

### Web Scraping

Thread pools are ideal for I/O-bound operations like web scraping:

```python
import requests
from bs4 import BeautifulSoup
from twat_mp import ThreadPool

def fetch_page_title(url):
    """Fetch the title of a webpage."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else "No title found"
        return {"url": url, "title": title, "status": response.status_code}
    except Exception as e:
        return {"url": url, "error": str(e), "status": None}

# List of URLs to scrape
urls = [
    "https://www.python.org",
    "https://www.github.com",
    "https://www.stackoverflow.com",
    "https://www.wikipedia.org",
    "https://www.reddit.com"
]

# Use ThreadPool for I/O-bound operations
with ThreadPool() as pool:
    results = list(pool.map(fetch_page_title, urls))

# Print results
for result in results:
    if "error" in result:
        print(f"Error fetching {result['url']}: {result['error']}")
    else:
        print(f"{result['url']} - {result['title']} (Status: {result['status']})")
```

### Data Processing with Pandas

Process large datasets in parallel chunks:

```python
import pandas as pd
import numpy as np
from twat_mp import ProcessPool

def process_chunk(chunk_data):
    """Process a chunk of data."""
    # Simulate some data processing
    chunk_data['processed'] = chunk_data['value'] * 2 + np.random.randn(len(chunk_data))
    chunk_data['category'] = pd.cut(chunk_data['processed'], 
                                    bins=[-np.inf, 0, 10, np.inf], 
                                    labels=['low', 'medium', 'high'])
    # Calculate some statistics
    result = {
        'chunk_id': chunk_data['chunk_id'].iloc[0],
        'mean': chunk_data['processed'].mean(),
        'median': chunk_data['processed'].median(),
        'std': chunk_data['processed'].std(),
        'count': len(chunk_data),
        'categories': chunk_data['category'].value_counts().to_dict()
    }
    return result

# Create a large DataFrame
n_rows = 1_000_000
df = pd.DataFrame({
    'value': np.random.randn(n_rows),
    'group': np.random.choice(['A', 'B', 'C', 'D'], n_rows)
})

# Split into chunks for parallel processing
chunk_size = 100_000
chunks = []
for i, chunk_start in enumerate(range(0, n_rows, chunk_size)):
    chunk_end = min(chunk_start + chunk_size, n_rows)
    chunk = df.iloc[chunk_start:chunk_end].copy()
    chunk['chunk_id'] = i
    chunks.append(chunk)

# Process chunks in parallel
with ProcessPool() as pool:
    results = list(pool.map(process_chunk, chunks))

# Combine results
summary = pd.DataFrame(results)
print(summary)
```

### Async File Processing

Combine async I/O with parallel processing:

```python
import asyncio
import aiofiles
import os
from twat_mp import AsyncMultiPool

async def count_words(filename):
    """Count words in a file asynchronously."""
    try:
        async with aiofiles.open(filename, 'r') as f:
            content = await f.read()
            word_count = len(content.split())
            return {"filename": filename, "word_count": word_count}
    except Exception as e:
        return {"filename": filename, "error": str(e)}

async def main():
    # Get all text files in a directory
    files = [os.path.join("documents", f) for f in os.listdir("documents") 
             if f.endswith(".txt")]
    
    # Process files in parallel
    async with AsyncMultiPool() as pool:
        results = await pool.map(count_words, files)
    
    # Calculate total word count
    total_words = sum(r.get("word_count", 0) for r in results)
    
    # Print results
    for result in results:
        if "error" in result:
            print(f"Error processing {result['filename']}: {result['error']}")
        else:
            print(f"{result['filename']}: {result['word_count']} words")
    
    print(f"Total word count: {total_words}")

# Run the async main function
asyncio.run(main())
```

## API Reference

For detailed API documentation, see the [API Reference](API_REFERENCE.md).

## License

MIT

---

_**Assistant**_

<think>I need to analyze the current `opero` API from the README and compare it to the `twat-mp` API that the user described. Then I'll create a plan for rewriting `opero` to align with what the user wants.

From the README, I can see that `opero` currently:
1. Provides a class-based `Orchestrator` API and a decorator-based `@orchestrate` API
2. Supports fallbacks, retries, rate limiting, and concurrency mechanisms
3. Handles both sync and async functions
4. Has several configuration classes for different resilience mechanisms

The user wants to simplify this into two main decorators:
1. `@opero` - a decorator that supports retrying and fallbacks
2. `@opmap` - a decorator similar to `twat-mp`'s `map` functions, but with added support for retrying, fallbacks, rate limiting, and concurrency variants

Let me plan how to rewrite `opero` to match this desired API.</think>I'll analyze both APIs and create a plan to rewrite `opero` according to your preferences.

## Current `opero` API Analysis

The current `opero` has:

1. A class-based `Orchestrator` that combines multiple resilience patterns
2. A decorator-based `@orchestrate` that wraps the Orchestrator's functionality 
3. Multiple configuration classes (`OrchestratorConfig`, `RetryConfig`, etc.)
4. Several resilience mechanisms (fallbacks, retries, rate limiting, concurrency)
5. A complex, deeply nested API that can be hard to understand

## `twat-mp` API Analysis

The `twat-mp` API is much clearer with:

1. Simple, focused decorators (`pmap`, `imap`, `amap`, `apmap`) for parallel operations
2. Clear pool abstractions (`ProcessPool`, `ThreadPool`, `AsyncMultiPool`)
3. A straightforward API without excessive configuration classes
4. Context managers for resource management

## Plan for Rewriting `opero`

Let me create a plan for rewriting `opero`:

---

_****_

```diff
  
  Tip: Periodically run `python ./cleanup.py status` to see results of lints and tests. Use `uv pip ...` not `pip ...`
+ 
+ ## Plan for Rewriting `opero`
+ 
+ ### 1. Restructure API into Two Primary Decorators
+ 
+ #### `@opero` Decorator
+ - Focus on providing simple retry and fallback mechanisms for single functions
+ - Remove excessive configuration complexity
+ - Allow simple configuration of retry attempts, backoff, and fallbacks
+ - Support both sync and async functions
+ 
+ #### `@opmap` Decorator
+ - Inspired by `twat-mp`'s map functions (`pmap`, `imap`, `amap`, `apmap`)
+ - Support parallel execution of functions over multiple inputs
+ - Include retry and fallback mechanisms
+ - Provide rate limiting capabilities
+ - Support various concurrency modes (process, thread, async)
+ 
+ ### 2. Simplify Configuration
+ 
+ - Remove the complex nested configuration classes
+ - Use simple function parameters with sensible defaults
+ - Make the API more intuitive with clear parameter names
+ - Accept callable fallbacks directly without wrapping in arrays
+ 
+ ### 3. Implementation Plan
+ 
+ 1. **Core Module Refactoring**
+    - Identify and preserve the essential resilience mechanisms
+    - Simplify the internal implementation
+    - Remove unnecessary abstraction layers
+ 
+ 2. **New Decorator API**
+    - Implement the `@opero` decorator for single function resilience
+    - Implement the `@opmap` decorator for parallel operations
+    - Ensure backward compatibility with the existing API
+ 
+ 3. **Concurrency Options**
+    - Implement ProcessPool, ThreadPool, and AsyncPool options
+    - Make it easy to switch between concurrency modes
+    - Support customization of worker count
+ 
+ 4. **Function Signatures**
+    ```python
+    # @opero decorator
+    @opero(
+        retries=3,                      # Number of retry attempts
+        backoff_factor=1.5,             # Backoff multiplier between retries
+        min_delay=0.1,                  # Minimum delay between retries (seconds)
+        max_delay=30,                   # Maximum delay between retries (seconds)
+        fallbacks=[fallback_func],      # Fallback functions to try on failure
+        retry_on=(Exception,)           # Exception types to retry on
+    )
+    def my_function(arg):
+        # Function implementation
+        pass
+ 
+    # @opmap decorator
+    @opmap(
+        mode="process",                 # "process", "thread", or "async"
+        workers=4,                      # Number of workers
+        retries=3,                      # Number of retry attempts
+        backoff_factor=1.5,             # Backoff multiplier between retries
+        min_delay=0.1,                  # Minimum delay between retries (seconds)
+        max_delay=30,                   # Maximum delay between retries (seconds)
+        fallbacks=[fallback_func],      # Fallback functions to try on failure
+        retry_on=(Exception,),          # Exception types to retry on
+        rate_limit=10,                  # Operations per second (if needed)
+        ordered=True                    # Whether to preserve input order in results
+    )
+    def process_item(item):
+        # Process a single item
+        return result
+    
+    # Usage
+    results = process_item([item1, item2, item3])
+    ```
+ 
+ ### 4. Testing Strategy
+ 
+ 1. Create unit tests for both decorators
+ 2. Test with various concurrency modes
+ 3. Test resilience mechanisms (fallbacks, retries)
+ 4. Test edge cases and error scenarios
+ 5. Ensure performance is comparable to or better than the previous implementation
+ 
+ ### 5. Documentation Updates
+ 
+ 1. Rewrite README.md with the new API
+ 2. Create clear, concise examples for both decorators
+ 3. Provide migration guide for users of the old API
+ 4. Document all parameters and their behavior
+ 
+ ### 6. Code Cleanup
+ 
+ 1. Remove deprecated functionality
+ 2. Simplify internal implementation
+ 3. Use modern Python features (match statements, type hints)
+ 4. Minimize dependencies
+ 
+ ### 7. Release Plan
+ 
+ 1. Implement core functionality first
+ 2. Release an alpha version for feedback
+ 3. Refine based on user feedback
+ 4. Complete documentation
+ 5. Release beta version
+ 6. Final release
+ 
+ ### Example Usage After Refactoring
+ 
+ ```python
+ from opero import opero, opmap
+ 
+ # Simple retry and fallback for a single function
+ @opero(retries=3, fallbacks=[fallback_func])
+ async def fetch_data(item_id):
+     # Implementation that might fail
+     ...
+ 
+ # Parallel processing with resilience
+ @opmap(mode="process", workers=4, retries=2, rate_limit=10)
+ def process_item(item):
+     # Process a single item
+     return result
+ 
+ # Simple usage
+ data = await fetch_data("item123")
+ 
+ # Parallel processing
+ results = process_item([item1, item2, item3, ...])
+ ```
+ 
+ ### Timeline
+ 
+ 1. Core refactoring: 1-2 weeks
+ 2. New decorator implementation: 1 week
+ 3. Testing and bug fixes: 1 week
+ 4. Documentation: 2-3 days
+ 5. Release process: 1 week
+ 
+ Total estimated time: ~4 weeks
  
  
```

---

_****_

## API Comparison & Recommendations

Based on my analysis of both the current `opero` API and the `twat-mp` API you prefer, I've created a plan to redesign `opero` with a cleaner, more intuitive interface.

### What's Wrong with the Current `opero` API

The current `opero` API has several issues:

1. **Over-engineered configuration** - The nested configuration classes (`OrchestratorConfig`, `RetryConfig`, etc.) create unnecessary complexity
2. **Confusing abstractions** - Concepts like `Orchestrator` and `FallbackChain` add mental overhead
3. **Inconsistent interfaces** - Mixing class-based and decorator-based APIs creates cognitive load
4. **Poor discoverability** - Parameter nesting makes it hard to discover available options
5. **Non-intuitive fallback handling** - Requiring fallbacks to be wrapped in lists is cumbersome

### Why `twat-mp`'s API is Better

The `twat-mp` API is superior because it:

1. **Uses clear, focused decorators** - Each decorator has a specific purpose
2. **Provides intuitive abstractions** - Pool types map directly to common parallelization patterns
3. **Has a consistent interface** - All decorators follow a similar pattern
4. **Offers simple configuration** - Parameters are passed directly to decorators
5. **Is discovery-friendly** - Available options are visible in the function signature

## Next Steps

I've added a comprehensive plan to your TODO.md that outlines:

1. Restructuring the API into two primary decorators
2. Simplifying the configuration approach
3. Implementing proper concurrency options
4. Creating a better function signature design
5. Testing strategies
6. Documentation updates
7. Code cleanup steps
8. A release plan with timeline

The plan includes example code showing how the new API would be used, making it clear how much simpler and more intuitive the new design will be.

Would you like me to elaborate on any specific part of the plan, or would you like to start implementing some of these changes?

---

_**User**_

for fallbacks, I want to have one "arg_fallback" arg which should take the name of the argument. 


def myfunction(prompt: str, model: str = "gpt-4"): 
  ...


@opero(arg_fallback=model)
def myfunction(prompt: str, model: list[str] = ["gpt-4", "gpt-3"]): 
  ... # This means that the function actually gets executed with model[0], and subsequent args of model are fallbacks



---

_**Assistant**_

<think>The user is suggesting an alternative approach to fallbacks in the `opero` API redesign. Instead of passing fallback functions, they want to specify a parameter that contains fallback values. Let me understand this:

1. They want an `arg_fallback` parameter in the `@opero` decorator
2. This parameter would take the name of an argument to the decorated function
3. The specified argument would be expected to contain a list of values
4. The function would be executed with the first value, and if it fails, it would retry with subsequent values

For example, in their case:
```python
@opero(arg_fallback="model")
def myfunction(prompt: str, model: list[str] = ["gpt-4", "gpt-3"]):
    ...
```

Here, the function would first try with `model="gpt-4"`, and if that fails, it would try with `model="gpt-3"`.

This is a clever approach that's different from the functional fallbacks I described in the plan. It's more data-driven and can be easier to use in cases where the fallback logic is simple (trying the same function with different parameter values).

I should update the TODO plan to include this approach.</think>I understand you want a different approach to fallbacks - instead of providing alternative functions, you want to specify a parameter whose values can serve as fallbacks. This is a great idea that makes the API much more intuitive for many common use cases!

Let me refine this concept in more detail:

## The `arg_fallback` Feature

With your approach, the `@opero` decorator would accept an `arg_fallback` parameter that:

1. Takes the name of a function parameter
2. Expects that parameter to contain a list/sequence of values
3. Tries the function first with the first value
4. If the function fails, retries with subsequent values in the list

This is a more data-driven approach to fallbacks that's very intuitive and powerful for many scenarios. Let me update the approach for both decorators:

---

_****_

```diff
  - Allow simple configuration of retry attempts, backoff, and fallbacks
  - Support both sync and async functions
+ - Support parameter-based fallbacks with `arg_fallback`
  
  #### 1.1.2. `@opmap` Decorator
  - Provide rate limiting capabilities
  - Support various concurrency modes (process, thread, async)
+ - Support parameter-based fallbacks with `arg_fallback`
  
  ### 1.2. Simplify Configuration
  - Use simple function parameters with sensible defaults
  - Make the API more intuitive with clear parameter names
- - Accept callable fallbacks directly without wrapping in arrays
+ - Support two fallback approaches:
+   1. Function-based fallbacks (alternative functions to try)
+   2. Parameter-based fallbacks (trying the same function with different parameter values)
  
  ### 1.3. Implementation Plan
     - Simplify the internal implementation
     - Remove unnecessary abstraction layers
+    - Implement parameter-based fallback mechanism
  
  2. **New Decorator API**
     - Implement the `@opero` decorator for single function resilience
     - Implement the `@opmap` decorator for parallel operations
     - Ensure backward compatibility with the existing API
+    - Support both fallback mechanisms
  
  3. **Concurrency Options**
  4. **Function Signatures**
     ```python
-    # @opero decorator
+    # @opero decorator with function-based fallbacks
     @opero(
         retries=3,                      # Number of retry attempts
         pass
  
+    # @opero decorator with parameter-based fallbacks
+    @opero(
+        retries=3,                      # Number of retry attempts
+        backoff_factor=1.5,             # Backoff multiplier between retries
+        min_delay=0.1,                  # Minimum delay between retries (seconds)
+        max_delay=30,                   # Maximum delay between retries (seconds)
+        arg_fallback="model",           # Parameter name containing fallback values
+        retry_on=(Exception,)           # Exception types to retry on
+    )
+    def call_llm(prompt: str, model: list[str] = ["gpt-4", "gpt-3.5"]):
+        # Will try with model="gpt-4" first, then model="gpt-3.5" if it fails
+        pass
+ 
     # @opmap decorator
     @opmap(
         max_delay=30,                   # Maximum delay between retries (seconds)
         fallbacks=[fallback_func],      # Fallback functions to try on failure
+        arg_fallback="model",           # Parameter name containing fallback values
         retry_on=(Exception,),          # Exception types to retry on
         rate_limit=10,                  # Operations per second (if needed)
         ordered=True                    # Whether to preserve input order in results
     )
-    def process_item(item):
+    def process_item(item, model: list[str] = ["gpt-4", "gpt-3.5"]):
         # Process a single item
         return result
  2. Test with various concurrency modes
  3. Test resilience mechanisms (fallbacks, retries)
- 4. Test edge cases and error scenarios
- 5. Ensure performance is comparable to or better than the previous implementation
+ 4. Test both function-based and parameter-based fallbacks
+ 5. Test edge cases and error scenarios
+ 6. Ensure performance is comparable to or better than the previous implementation
  
  ### 1.5. Documentation Updates
  3. Provide migration guide for users of the old API
  4. Document all parameters and their behavior
+ 5. Include examples of both fallback approaches
  
  ### 1.6. Code Cleanup
  from opero import opero, opmap
  
+ # Using parameter-based fallbacks
+ @opero(arg_fallback="model")
+ async def call_llm(prompt: str, model: list[str] = ["gpt-4", "gpt-3.5"]):
+     # Will try with model="gpt-4" first, then model="gpt-3.5" if it fails
+     response = await api_call(prompt=prompt, model=model)
+     return response
+ 
  # Simple retry and fallback for a single function
  @opero(retries=3, fallbacks=[fallback_func])
      return result
  
- # Simple usage
- data = await fetch_data("item123")
+ # Parameter-based fallbacks with parallel processing
+ @opmap(mode="thread", workers=4, arg_fallback="api_key")
+ def call_api(item, api_key: list[str] = ["primary_key", "backup_key", "emergency_key"]):
+     # Will try each API key in order if previous ones fail
+     return make_request(item, api_key=api_key)
  
- # Parallel processing
- results = process_item([item1, item2, item3, ...])
+ # Usage examples
+ data = await call_llm("Tell me about Python")  # Will try with gpt-4, fallback to gpt-3.5
+ results = call_api([item1, item2, item3])      # Process items in parallel with key fallbacks
  ```
  
  
  Total estimated time: ~4 weeks
+ 
+ ### 1.10. Implementation Details for Parameter-Based Fallbacks
+ 
+ To implement parameter-based fallbacks, the decorator will:
+ 
+ 1. Parse and validate the decorated function's signature
+ 2. Check if the specified `arg_fallback` parameter exists and has a sequence type
+ 3. When the function is called:
+    - Store the original parameter value (list of fallback options)
+    - Try executing the function with the first value in the list
+    - If an exception occurs, retry with the next value in the list
+    - Continue until success or all values are exhausted
+    
+ This implementation must handle:
+ - Proper type annotation preservation
+ - Documentation generation
+ - Graceful failure if the parameter isn't a sequence
+ - Integration with other resilience mechanisms (retries, rate limiting)
  
  
```

---

_****_

## Parameter-Based Fallbacks: A Better Approach!

Your suggestion for `arg_fallback` is excellent! It provides a much more intuitive and elegant approach to handling fallbacks in many common scenarios. Rather than requiring separate fallback functions, it lets you specify a parameter that already contains alternative options to try.

This approach has several advantages:

1. **More intuitive**: It aligns with how people naturally think about fallbacks
2. **Less code duplication**: No need to create separate fallback functions
3. **Data-driven**: The fallback logic is expressed in data rather than code
4. **Type-safe**: Works well with type annotations
5. **Context preservation**: Maintains the context of the original function call

I've updated the TODO plan to incorporate your `arg_fallback` approach. Here's how it would work:

```python
@opero(arg_fallback="model")
def call_llm(prompt: str, model: list[str] = ["gpt-4", "gpt-3.5"]):
    # First execution: model = "gpt-4"
    # If that fails: model = "gpt-3.5"
    response = call_api(prompt=prompt, model=model)
    return response
```

Both decorators (`@opero` and `@opmap`) would support this mechanism, making it easy to:

1. Try different LLM models in sequence
2. Attempt with different API keys if the primary one fails
3. Fall back to different services or endpoints
4. Use varying parameters (temperature, max_tokens, etc.)

## Implementation Considerations

The implementation would need to:

1. Inspect the function signature to confirm the parameter exists
2. Check that the parameter value is a sequence-like object
3. Sequentially try the function with each value in the parameter
4. Handle type annotation preservation properly

I've also added an implementation details section to the TODO that outlines how this would work internally.

## Both Fallback Approaches

The plan now supports two fallback approaches:

1. **Parameter-based fallbacks** (your suggestion): Uses `arg_fallback` to try the same function with different parameter values
2. **Function-based fallbacks**: Uses `fallbacks` to try different functions if the primary function fails

This gives users flexibility to choose the approach that best suits their needs.

Would you like me to expand on any other aspects of the parameter-based fallback approach? Or would you like to explore other improvements to the API design?

---

_**User**_

Function-based fallbacks: Uses fallbacks to try different functions if the primary function fails — I DON’T WANT THIS, THIS SHOUDLD BE REMOVED

---

_**Assistant**_

<think>The user clearly wants to remove the function-based fallbacks approach completely and only keep the parameter-based fallbacks (`arg_fallback`). Let me update the TODO plan to reflect this preference by:

1. Removing all mentions of function-based fallbacks
2. Clarifying that only parameter-based fallbacks will be supported
3. Removing the `fallbacks` parameter from all examples
4. Updating relevant sections that discuss both approaches

This is a good simplification that makes the API even cleaner and more focused.</think>I understand your preference - you want to completely remove the function-based fallbacks approach and focus only on the parameter-based fallbacks with `arg_fallback`. Let me update the plan to reflect this:

---

_****_

```diff
  - Focus on providing simple retry and fallback mechanisms for single functions
  - Remove excessive configuration complexity
- - Allow simple configuration of retry attempts, backoff, and fallbacks
+ - Allow simple configuration of retry attempts and backoff
  - Support both sync and async functions
  - Support parameter-based fallbacks with `arg_fallback`
  
- #### 1.1.2. `@opmap` Decorator
+ #### 1.1.2. `@opmap` Decorator
  - Inspired by `twat-mp`'s map functions (`pmap`, `imap`, `amap`, `apmap`)
  - Support parallel execution of functions over multiple inputs
  - Use simple function parameters with sensible defaults
  - Make the API more intuitive with clear parameter names
- - Support two fallback approaches:
-   1. Function-based fallbacks (alternative functions to try)
-   2. Parameter-based fallbacks (trying the same function with different parameter values)
+ - Focus exclusively on parameter-based fallbacks (trying the same function with different parameter values)
  
  ### 1.3. Implementation Plan
  2. **New Decorator API**
     - Implement the `@opero` decorator for single function resilience
-    - Implement the `@opmap` decorator for parallel operations
+    - Implement the `@opmap` decorator for parallel operations
     - Ensure backward compatibility with the existing API
-    - Support both fallback mechanisms
+    - Support parameter-based fallbacks exclusively
  
  3. **Concurrency Options**
  4. **Function Signatures**
     ```python
-    # @opero decorator with function-based fallbacks
-    @opero(
-        retries=3,                      # Number of retry attempts
-        backoff_factor=1.5,             # Backoff multiplier between retries
-        min_delay=0.1,                  # Minimum delay between retries (seconds)
-        max_delay=30,                   # Maximum delay between retries (seconds)
-        fallbacks=[fallback_func],      # Fallback functions to try on failure
-        retry_on=(Exception,)           # Exception types to retry on
-    )
-    def my_function(arg):
-        # Function implementation
-        pass
- 
     # @opero decorator with parameter-based fallbacks
     @opero(
         pass
  
-    # @opmap decorator
-    @opmap(
+    # @opmap decorator
+    @opmap(
         mode="process",                 # "process", "thread", or "async"
         workers=4,                      # Number of workers
         min_delay=0.1,                  # Minimum delay between retries (seconds)
         max_delay=30,                   # Maximum delay between retries (seconds)
-        fallbacks=[fallback_func],      # Fallback functions to try on failure
         arg_fallback="model",           # Parameter name containing fallback values
         retry_on=(Exception,),          # Exception types to retry on
  2. Test with various concurrency modes
  3. Test resilience mechanisms (fallbacks, retries)
- 4. Test both function-based and parameter-based fallbacks
+ 4. Test parameter-based fallbacks thoroughly
  5. Test edge cases and error scenarios
  6. Ensure performance is comparable to or better than the previous implementation
  3. Provide migration guide for users of the old API
  4. Document all parameters and their behavior
- 5. Include examples of both fallback approaches
+ 5. Include examples of parameter-based fallbacks
  
  ### 1.6. Code Cleanup
  
  ```python
- from opero import opero, opmap
+ from opero import opero, opmap
  
  # Using parameter-based fallbacks
      return response
  
- # Simple retry and fallback for a single function
- @opero(retries=3, fallbacks=[fallback_func])
+ # Simple retry with no fallbacks
+ @opero(retries=3)
  async def fetch_data(item_id):
      # Implementation that might fail
      ...
  
  # Parallel processing with resilience
- @opmap(mode="process", workers=4, retries=2, rate_limit=10)
+ @opmap(mode="process", workers=4, retries=2, rate_limit=10)
  def process_item(item):
      # Process a single item
      return result
  
  # Parameter-based fallbacks with parallel processing
- @opmap(mode="thread", workers=4, arg_fallback="api_key")
+ @opmap(mode="thread", workers=4, arg_fallback="api_key")
  def call_api(item, api_key: list[str] = ["primary_key", "backup_key", "emergency_key"]):
      # Will try each API key in order if previous ones fail
```

---

_****_

## Updated Plan: Parameter-Based Fallbacks Only

I've revised the plan according to your direction to completely remove function-based fallbacks. This is a great simplification that makes the API even cleaner and more focused!

### Key Changes to the Plan:

1. **Removed function-based fallbacks completely** - No more `fallbacks` parameter
2. **Focused exclusively on parameter-based fallbacks** - Only `arg_fallback` is supported
3. **Simplified examples** - All examples now use only parameter-based fallbacks
4. **Renamed everything consistently** - Ensured we're using `opmap` (not `opmap`) throughout

### Benefits of This Approach:

By focusing exclusively on parameter-based fallbacks, your API will be:

1. **More intuitive** - The fallback logic is expressed in data, where it belongs
2. **Simpler to understand** - Users only need to learn one fallback mechanism
3. **More type-safe** - Works naturally with Python's type system
4. **Easier to implement** - The implementation can be more focused and robust
5. **More aligned with real-world use cases** - Handles common scenarios like API keys and model fallbacks elegantly

### Example Usage:

```python
# Single function with model fallbacks
@opero(arg_fallback="model")
async def call_llm(prompt: str, model: list[str] = ["gpt-4", "gpt-3.5"]):
    response = await api_call(prompt=prompt, model=model)
    return response

# Parallel API calls with key fallbacks
@opmap(mode="thread", workers=4, arg_fallback="api_key")
def call_api(item, api_key: list[str] = ["primary_key", "backup_key"]):
    return make_request(item, api_key=api_key)

# Usage is clean and intuitive
results = call_api([item1, item2, item3])
```

This approach is much cleaner and more intuitive than the original complex configuration system in `opero`. It gives users the power of resilient operations without the cognitive overhead of a complex API.

Is there anything specific about the implementation of parameter-based fallbacks you'd like me to elaborate on, or would you like to address any other aspects of the redesign?

---

_**User**_

Analyze the full codebase of @REPO_CONTENT.txt and extend @TODO.md to be very detailed and precise

---

_**Assistant**_

<think>I don't see an attached file named "@REPO_CONTENT.txt", and I need to analyze the codebase to provide a detailed plan. Let me check if I can see the repository content through other means.</think>I need to analyze the repository to provide a detailed plan. Let me examine the codebase first.

---

_****_

<details>
            <summary>Listed current directory • **26** results</summary>
        
| Name |
|-------|
| 📄 `TODO.md` |
| 📄 `CLEANUP.txt` |
| 📄 `REPO_CONTENT.txt` |
| 📁 `.git` |
| 📁 `.venv` |
| 📄 `README.md` |
| 📄 `CHANGELOG.md` |
| 📄 `cleanup.py` |
| 📄 `pyproject.toml` |
| 📁 `tests` |
| 📁 `src` |
| 📄 `.pre-commit-config.yaml` |
| 📄 `.coverage` |
| 📄 `LOG.md` |
| 📁 `dist` |
| 📄 `.DS_Store` |
| 📄 `package.toml` |
| 📄 `LICENSE` |
| 📁 `.ruff_cache` |
| 📁 `.cursor` |
| 📄 `uv.lock` |
| 📁 `.benchmarks` |
| 📁 `.pytest_cache` |
| 📁 `.specstory` |
| 📁 `.github` |
| 📄 `.gitignore` |

</details>

---

_****_

Great! I can see there's a `REPO_CONTENT.txt` file that likely contains the codebase content. Let's examine it.

---

_****_

Read file: REPO_CONTENT.txt

---

_****_

Let me see more of the codebase, specifically focusing on the source files in the `src/opero` directory to understand the current implementation.

---

_****_

Read file: REPO_CONTENT.txt

---

_****_

Let me continue reading to understand the core functionality of opero better:

---

_****_

Read file: REPO_CONTENT.txt

---

_****_

Let me read more of the file to see the remaining content:

---

_****_

Read file: REPO_CONTENT.txt

---

_****_

Let me check the pyproject.toml file to understand the package configuration:

---

_****_

Read file: pyproject.toml

---

_****_

Based on my analysis of the codebase, let me update the plan with detailed implementation steps. I'll modify the TODO.md file to include a comprehensive plan:

---

_****_

```diff
  - Support parameter-based fallbacks with `arg_fallback`
  
- #### 1.1.2. `@opmap` Decorator
+ #### 1.1.2. `@opmap` Decorator
  - Inspired by `twat-mp`'s map functions (`pmap`, `imap`, `amap`, `apmap`)
  - Support parallel execution of functions over multiple inputs
  2. **New Decorator API**
     - Implement the `@opero` decorator for single function resilience
-    - Implement the `@opmap` decorator for parallel operations
+    - Implement the `@opmap` decorator for parallel operations
     - DROP backward compatibility with the existing API, it's not important
     - Support parameter-based fallbacks exclusively
         pass
  
-    # @opmap decorator
-    @opmap(
+    # @opmap decorator
+    @opmap(
         mode="process",                 # "process", "thread", or "async"
         workers=4,                      # Number of workers
  
  ```python
- from opero import opero, opmap
+ from opero import opero, opmap
  
  # Using parameter-based fallbacks
  
  # Parallel processing with resilience
- @opmap(mode="process", workers=4, retries=2, rate_limit=10)
+ @opmap(mode="process", workers=4, retries=2, rate_limit=10)
  def process_item(item):
      # Process a single item
      return result
  
  # Parameter-based fallbacks with parallel processing
- @opmap(mode="thread", workers=4, arg_fallback="api_key")
+ @opmap(mode="thread", workers=4, arg_fallback="api_key")
  def call_api(item, api_key: list[str] = ["primary_key", "backup_key", "emergency_key"]):
      # Will try each API key in order if previous ones fail
  - Graceful failure if the parameter isn't a sequence
  - Integration with other resilience mechanisms (retries, rate limiting)
+ 
+ ## 2. Detailed Implementation Steps
+ 
+ ### 2.1. Create New File Structure
+ 
+ 1. Create new core modules:
+    ```
+    src/opero/
+    ├── __init__.py            # Re-exports public API
+    ├── _version.py            # Version information
+    ├── decorators/            # New directory for decorators
+    │   ├── __init__.py        # Re-exports decorators
+    │   ├── opero.py           # @opero decorator implementation
+    │   └── opmap.py        # @opmap decorator implementation
+    ├── core/                  # Core functionality
+    │   ├── __init__.py
+    │   ├── retry.py           # Retry mechanisms
+    │   ├── fallback.py        # Parameter-based fallback implementation
+    │   └── rate_limit.py      # Rate limiting mechanisms
+    ├── concurrency/           # Concurrency implementations
+    │   ├── __init__.py
+    │   ├── base.py            # Base pool interface
+    │   ├── process.py         # Process pool implementation
+    │   ├── thread.py          # Thread pool implementation
+    │   └── asyncio.py         # Async pool implementation
+    └── utils/                 # Utility functions
+        ├── __init__.py
+        ├── async_utils.py     # Async utilities
+        └── logging.py         # Logging utilities
+    ```
+ 
+ 2. Rename existing modules to avoid conflicts during development:
+    - `core.py` → `_old_core.py`
+    - `decorators.py` → `_old_decorators.py`
+    - etc.
+ 
+ ### 2.2. Implement Parameter-Based Fallback Mechanism
+ 
+ 1. Create `core/fallback.py` with key features:
+    ```python
+    from typing import Any, Callable, TypeVar, ParamSpec, cast, get_type_hints, Sequence
+    import inspect
+    import functools
+    import asyncio
+    
+    P = ParamSpec('P')
+    R = TypeVar('R')
+    
+    class ArgFallbackError(Exception):
+        """Error raised when all parameter-based fallbacks have been exhausted."""
+        pass
+    
+    def get_parameter_fallbacks(func: Callable, arg_name: str, args: tuple, kwargs: dict) -> list:
+        """Extract fallback options from function arguments."""
+        sig = inspect.signature(func)
+        param_dict = dict(zip(list(sig.parameters.keys())[:len(args)], args))
+        param_dict.update(kwargs)
+        
+        if arg_name not in param_dict:
+            raise ValueError(f"Parameter '{arg_name}' not found in function signature")
+            
+        fallback_values = param_dict[arg_name]
+        if not isinstance(fallback_values, Sequence) or isinstance(fallback_values, (str, bytes)):
+            raise ValueError(f"Parameter '{arg_name}' must be a sequence (list, tuple)")
+            
+        return list(fallback_values)
+    
+    async def try_with_arg_fallback(
+        func: Callable[P, R], 
+        arg_name: str,
+        args: P.args,
+        kwargs: P.kwargs,
+    ) -> R:
+        """Try to execute a function with parameter-based fallbacks."""
+        fallback_values = get_parameter_fallbacks(func, arg_name, args, kwargs)
+        if not fallback_values:
+            raise ValueError(f"No fallback values found in parameter '{arg_name}'")
+        
+        # Convert args to a list so we can modify it if needed
+        args_list = list(args)
+        
+        # Find if the fallback argument is in args or kwargs
+        sig = inspect.signature(func)
+        param_names = list(sig.parameters.keys())
+        
+        last_error = None
+        for i, value in enumerate(fallback_values):
+            try:
+                # Update the argument with the current fallback value
+                if arg_name in kwargs:
+                    kwargs[arg_name] = value
+                elif arg_name in param_names:
+                    arg_index = param_names.index(arg_name)
+                    if arg_index < len(args_list):
+                        args_list[arg_index] = value
+                    else:
+                        kwargs[arg_name] = value
+                
+                # Call the function with updated arguments
+                if asyncio.iscoroutinefunction(func):
+                    return await func(*args_list, **kwargs)
+                else:
+                    return func(*args_list, **kwargs)
+            except Exception as e:
+                last_error = e
+                continue
+        
+        # If we've exhausted all fallbacks, raise an error
+        if last_error:
+            raise ArgFallbackError(f"All fallback values for '{arg_name}' failed") from last_error
+        else:
+            raise ArgFallbackError(f"No fallback values provided for '{arg_name}'")
+    ```
+ 
+ ### 2.3. Implement the New Decorators
+ 
+ 1. Create `decorators/opero.py`:
+    ```python
+    from typing import Any, Callable, TypeVar, ParamSpec, Optional, Union, Type, Tuple
+    import functools
+    import inspect
+    import asyncio
+    
+    from ..core.fallback import try_with_arg_fallback
+    from ..core.retry import retry_async, RetryConfig
+    
+    P = ParamSpec('P')
+    R = TypeVar('R')
+    
+    def opero(
+        retries: int = 3,
+        backoff_factor: float = 1.5,
+        min_delay: float = 0.1,
+        max_delay: float = 30.0,
+        arg_fallback: Optional[str] = None,
+        retry_on: Union[Type[Exception], Tuple[Type[Exception], ...]] = (Exception,),
+    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
+        """
+        Decorator for adding resilience to functions with retries and parameter-based fallbacks.
+        
+        Args:
+            retries: Number of retry attempts before giving up.
+            backoff_factor: Multiplier for exponential backoff between retries.
+            min_delay: Minimum delay between retries in seconds.
+            max_delay: Maximum delay between retries in seconds.
+            arg_fallback: Name of the parameter containing fallback values.
+            retry_on: Exception type(s) that should trigger a retry.
+            
+        Returns:
+            Decorated function with enhanced resilience.
+        """
+        retry_config = RetryConfig(
+            max_attempts=retries,
+            wait_multiplier=backoff_factor,
+            wait_min=min_delay,
+            wait_max=max_delay,
+            retry_exceptions=retry_on if isinstance(retry_on, tuple) else (retry_on,),
+        )
+        
+        def decorator(func: Callable[P, R]) -> Callable[P, R]:
+            @functools.wraps(func)
+            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
+                if arg_fallback:
+                    try:
+                        return await try_with_arg_fallback(
+                            lambda *a, **kw: retry_async(func, retry_config, *a, **kw),
+                            arg_fallback,
+                            args,
+                            kwargs
+                        )
+                    except Exception as e:
+                        if retries > 0:
+                            return await retry_async(func, retry_config, *args, **kwargs)
+                        raise e
+                else:
+                    return await retry_async(func, retry_config, *args, **kwargs)
+            
+            @functools.wraps(func)
+            def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
+                return asyncio.run(async_wrapper(*args, **kwargs))
+            
+            if asyncio.iscoroutinefunction(func):
+                return async_wrapper
+            else:
+                return sync_wrapper
+                
+        return decorator
+    ```
+ 
+ 2. Create `decorators/opmap.py`:
+    ```python
+    from typing import Any, Callable, TypeVar, ParamSpec, Optional, Union, Type, Tuple, List, Iterable
+    import functools
+    import inspect
+    import asyncio
+    
+    from ..core.fallback import try_with_arg_fallback
+    from ..core.retry import retry_async, RetryConfig
+    from ..core.rate_limit import RateLimiter
+    from ..concurrency.base import Pool, get_pool
+    
+    P = ParamSpec('P')
+    R = TypeVar('R')
+    T = TypeVar('T')  # Input item type
+    
+    def opmap(
+        mode: str = "process",
+        workers: int = None,
+        retries: int = 3,
+        backoff_factor: float = 1.5,
+        min_delay: float = 0.1,
+        max_delay: float = 30.0,
+        arg_fallback: Optional[str] = None,
+        retry_on: Union[Type[Exception], Tuple[Type[Exception], ...]] = (Exception,),
+        rate_limit: Optional[float] = None,
+        ordered: bool = True,
+    ) -> Callable[[Callable[..., R]], Callable[[Iterable[T]], List[R]]]:
+        """
+        Decorator for parallel processing with resilience features.
+        
+        Args:
+            mode: Concurrency mode: "process", "thread", or "async".
+            workers: Number of worker processes/threads.
+            retries: Number of retry attempts before giving up.
+            backoff_factor: Multiplier for exponential backoff between retries.
+            min_delay: Minimum delay between retries in seconds.
+            max_delay: Maximum delay between retries in seconds.
+            arg_fallback: Name of the parameter containing fallback values.
+            retry_on: Exception type(s) that should trigger a retry.
+            rate_limit: Maximum operations per second.
+            ordered: Whether to preserve the order of results.
+            
+        Returns:
+            Decorated function that processes items in parallel.
+        """
+        retry_config = RetryConfig(
+            max_attempts=retries,
+            wait_multiplier=backoff_factor,
+            wait_min=min_delay,
+            wait_max=max_delay,
+            retry_exceptions=retry_on if isinstance(retry_on, tuple) else (retry_on,),
+        )
+        
+        def decorator(func: Callable[..., R]) -> Callable[[Iterable[T]], List[R]]:
+            async def process_item(item: T) -> R:
+                """Process a single item with retries and fallbacks."""
+                if arg_fallback:
+                    try:
+                        return await try_with_arg_fallback(
+                            lambda *a, **kw: retry_async(func, retry_config, *a, **kw),
+                            arg_fallback,
+                            (item,),
+                            {}
+                        )
+                    except Exception as e:
+                        if retries > 0:
+                            return await retry_async(func, retry_config, item)
+                        raise e
+                else:
+                    return await retry_async(func, retry_config, item)
+            
+            async def process_with_rate_limit(item: T) -> R:
+                """Process an item with rate limiting."""
+                if rate_limit:
+                    limiter = RateLimiter(rate_limit)
+                    async with limiter:
+                        return await process_item(item)
+                return await process_item(item)
+                
+            async def process_items(items: Iterable[T]) -> List[R]:
+                """Process multiple items in parallel."""
+                items_list = list(items)
+                async with get_pool(mode, workers) as pool:
+                    results = await pool.map(process_with_rate_limit, items_list)
+                return results
+            
+            @functools.wraps(func)
+            def wrapper(items: Iterable[T]) -> List[R]:
+                return asyncio.run(process_items(items))
+                
+            return wrapper
+        
+        return decorator
+    ```
+ 
+ ### 2.4. Implement Pool Abstractions
+ 
+ 1. Create `concurrency/base.py`:
+    ```python
+    from typing import Any, Callable, TypeVar, Generic, List, Iterable, Protocol, runtime_checkable
+    import asyncio
+    
+    T = TypeVar('T')  # Input type
+    R = TypeVar('R')  # Return type
+    
+    @runtime_checkable
+    class Pool(Protocol[T, R]):
+        """Protocol defining the interface for parallel execution pools."""
+        
+        async def map(self, func: Callable[[T], R], items: Iterable[T]) -> List[R]:
+            """Execute a function over multiple items in parallel."""
+            ...
+    
+    async def get_pool(mode: str, workers: int = None) -> Pool:
+        """Factory function to get an appropriate pool based on the mode."""
+        if mode == "process":
+            from .process import ProcessPool
+            return ProcessPool(workers)
+        elif mode == "thread":
+            from .thread import ThreadPool
+            return ThreadPool(workers)
+        elif mode == "async":
+            from .asyncio import AsyncPool
+            return AsyncPool(workers)
+        else:
+            raise ValueError(f"Unknown pool mode: {mode}")
+    ```
+ 
+ 2. Implement concrete pool classes in separate files (`process.py`, `thread.py`, `asyncio.py`)
+ 
+ ### 2.5. Testing Details
+ 
+ 1. Create test files for each new module:
+    ```
+    tests/
+    ├── decorators/
+    │   ├── test_opero.py
+    │   └── test_opmap.py
+    ├── core/
+    │   ├── test_fallback.py
+    │   └── test_retry.py
+    └── concurrency/
+        ├── test_process.py
+        ├── test_thread.py
+        └── test_async.py
+    ```
+ 
+ 2. Test specific scenarios for parameter-based fallbacks:
+    ```python
+    # In tests/core/test_fallback.py
+    
+    async def test_arg_fallback_successful():
+        """Test that the first fallback option works."""
+        
+    async def test_arg_fallback_uses_second_option():
+        """Test that the second option is used when the first fails."""
+        
+    async def test_arg_fallback_exhausted():
+        """Test behavior when all fallback options fail."""
+        
+    async def test_invalid_arg_fallback_parameter():
+        """Test handling of invalid parameter names."""
+        
+    async def test_non_sequence_arg_fallback():
+        """Test handling of non-sequence fallback parameters."""
+    ```
+ 
+ ### 2.6. Documentation Updates
+ 
+ 1. Update README.md with new sections:
+    - Introduction to the new API design
+    - Examples of `@opero` usage with parameter-based fallbacks
+    - Examples of `@opmap` usage for parallel processing
+    - Comparison with the old API (for existing users)
+    - FAQ section addressing common questions
+ 
+ 2. Create detailed API reference for both decorators including all parameters
+ 
+ ### 2.7. Dependency Management
+ 
+ 1. Update `pyproject.toml` to reflect new dependencies:
+    ```toml
+    [project]
+    dependencies = [
+        "tenacity>=8.0.0",        # For retry functionality
+        "asynciolimiter>=1.0.0",  # For rate limiting
+    ]
+    
+    [project.optional-dependencies]
+    process = [
+        "pathos>=0.3.0",          # Better process pool implementation
+    ]
+    async = [
+        "aiomultiprocess>=0.9.0",  # Async multiprocessing
+    ]
+    all = [
+        "pathos>=0.3.0",
+        "aiomultiprocess>=0.9.0",
+    ]
+    ```
+ 
+ ## 3. Migration Strategy
+ 
+ 1. New code should be developed alongside existing code
+ 2. Rename old modules with underscore prefix (`_old_*.py`)
+ 3. Gradually refactor tests to use new API
+ 4. Release alpha version with both old and new APIs
+ 5. Get feedback and finalize the new API
+ 6. Release final version with only the new API
+ 
+ ## 4. Success Criteria
+ 
+ The rewrite will be considered successful if:
+ 
+ 1. Code is significantly simpler (measured by complexity metrics)
+ 2. API is more intuitive and easier to understand
+ 3. Tests pass with the same or better coverage
+ 4. Performance is comparable or improved
+ 5. Documentation is clear and comprehensive
  
  
```

---

_****_

## Your Detailed Opero API Rewrite Plan

Based on my comprehensive analysis of the current codebase, I've created a detailed plan for rewriting the `opero` package with the new API approach you requested. This plan now provides concrete implementation details to guide the development process.

### Key Features of the New Plan

1. **More Detailed Implementation Guide**
   - Complete file structure for the new organization
   - Actual code examples for core functionality
   - Detailed API signatures with docstrings
   - Testing strategy with specific test cases

2. **Parameter-Based Fallbacks Implementation**
   - Complete implementation of the `arg_fallback` mechanism
   - Handling of edge cases and error conditions
   - Signature inspection and parameter handling

3. **Practical Concurrency Options**
   - Clear separation of concurrency modes
   - Protocol-based interface for pool implementations
   - Integration with retry and fallback mechanisms

4. **Streamlined API Design**
   - Two focused decorators (`@opero` and `@opmap`)
   - Simple, flat parameter structure
   - Intuitive defaults for common use cases
   - No function-based fallbacks as requested

### Highlighted Sections:

1. **File Structure** (Section 2.1)
   - Organized by functionality (decorators, core, concurrency, utils)
   - Clean separation of concerns
   - Migration path with minimal disruption

2. **Parameter-Based Fallback Implementation** (Section 2.2)
   - Complete implementation for extracting fallback options
   - Handling of args/kwargs with proper signature inspection
   - Error handling for edge cases

3. **Decorator Implementations** (Section 2.3)
   - Full code for both decorators with proper typing
   - Integration of retry, fallback, and rate limiting
   - Support for both sync and async functions

4. **Concurrency Abstractions** (Section 2.4)
   - Protocol-based interface for different pool types
   - Factory function for obtaining appropriate pools
   - Clean async context management

5. **Migration Strategy** (Section 3)
   - Practical approach to transition with minimal disruption
   - Maintaining both old and new APIs during transition
   - Clear path to final implementation

This plan provides a comprehensive roadmap for implementing the new API while ensuring it's well-tested, properly documented, and maintains the core functionality of the existing package.

Would you like me to elaborate on any specific aspect of this implementation plan?

---

_**User**_

Incorporate caching as well, using twat-cache


# twat-cache

A flexible caching utility package for Python functions that provides a unified interface for caching function results using various high-performance backends.

## Features

- Simple decorator interface for caching function results
- Multiple caching backends with automatic selection:
  1. `cachebox` - Very fast Rust-based cache (optional)
  2. `cachetools` - Flexible in-memory caching (optional)
  3. `aiocache` - Async-capable caching (optional)
  4. `klepto` - Scientific computing caching (optional)
  5. `diskcache` - SQL-based disk cache (optional)
  6. `joblib` - Efficient array caching (optional)
  7. `redis` - Distributed caching with Redis (optional)
  8. Memory-based LRU cache (always available)
- Automatic cache directory management
- Type hints and modern Python features
- Lazy backend loading - only imports what you use
- Automatic backend selection based on availability and use case
- Smart backend selection based on data characteristics
- TTL support for cache expiration
- Multiple eviction policies (LRU, LFU, FIFO, RR)
- Async function support
- Compression options for large data
- Secure file permissions for sensitive data
- Hybrid caching with automatic backend switching
- Context management for cache engines
- Comprehensive test suite for all components

## Recent Updates (v2.3.0)

### Enhanced Context Management

The context management system has been significantly improved:
- Better error handling and resource cleanup
- Support for explicit engine selection
- Simplified API for temporary cache configurations
- Automatic cleanup of resources even when exceptions occur

```python
# Example of improved context management
from twat_cache import CacheContext

# Create a context with explicit engine selection
with CacheContext(engine_name="redis", namespace="user_data") as cache:
    # Use the cache within the context
    cache.set("user:1001", {"name": "John", "role": "admin"})
    user = cache.get("user:1001")
    
    # Resources are automatically cleaned up when exiting the context
```

### Refined Backend Selection

The backend selection strategy has been further enhanced:
- More accurate data type detection for optimal backend selection
- Improved fallback mechanisms when preferred backends are unavailable
- Better handling of edge cases for various data types
- Enhanced performance for frequently accessed items

### Comprehensive Documentation

Documentation has been expanded with:
- Detailed examples for all cache backends
- Step-by-step guides for common use cases
- API reference with complete parameter descriptions
- Best practices for cache configuration

## Installation

Basic installation with just LRU caching:
```bash
pip install twat-cache
```

With all optional backends:
```bash
pip install twat-cache[all]
```

Or install specific backends:
```bash
pip install twat-cache[cachebox]     # For Rust-based high-performance cache
pip install twat-cache[cachetools]   # For flexible in-memory caching
pip install twat-cache[aiocache]     # For async-capable caching
pip install twat-cache[klepto]       # For scientific computing caching
pip install twat-cache[diskcache]    # For SQL-based disk caching
pip install twat-cache[joblib]       # For efficient array caching
pip install twat-cache[redis]        # For distributed caching with Redis
```

## Usage

### Basic Memory Caching

For simple in-memory caching with LRU eviction:

```python
from twat_cache import mcache

@mcache(maxsize=100)  # Cache up to 100 items
def expensive_function(x: int) -> int:
    # Expensive computation here
    return x * x

# First call computes
result1 = expensive_function(5)  # Computes 25

# Second call uses cache
result2 = expensive_function(5)  # Returns cached 25
```

### Disk-Based Caching

For persistent caching using SQLite:

```python
from twat_cache import bcache

@bcache(
    folder_name="my_cache",  # Cache directory name
    maxsize=1_000_000,       # Max cache size in bytes
    ttl=3600,               # Cache entries expire after 1 hour
    use_sql=True,           # Use SQLite backend
    secure=True,            # Use secure file permissions
)
def expensive_function(x: int) -> int:
    return x * x
```

### Redis Distributed Caching

For distributed caching with Redis:

```python
from twat_cache import ucache

@ucache(
    preferred_engine="redis",
    folder_name="redis_cache",  # Used as Redis namespace
    ttl=3600,                  # Cache entries expire after 1 hour
    compress=True,             # Enable compression
)
def expensive_function(x: int) -> int:
    return x * x
```

### File-Based Caching

For efficient caching of large objects like NumPy arrays:

```python
from twat_cache import fcache
import numpy as np

@fcache(
    folder_name="array_cache",
    compress=True,           # Enable compression
    secure=True,            # Use secure file permissions
)
def process_array(data: np.ndarray) -> np.ndarray:
    # Expensive array processing here
    return data * 2
```

### Async Caching

For async functions with Redis or memory backend:

```python
from twat_cache import ucache

@ucache(use_async=True)
async def fetch_data(url: str) -> dict:
    # Async web request here
    return {"data": "..."}

# First call fetches
data1 = await fetch_data("https://api.example.com")

# Second call uses cache
data2 = await fetch_data("https://api.example.com")
```

### Universal Caching

Let the library choose the best backend:

```python
from twat_cache import ucache

@ucache(
    folder_name="cache",     # Optional - uses disk cache if provided
    maxsize=1000,           # Optional - limits cache size
    ttl=3600,              # Optional - entries expire after 1 hour
    policy="lru",          # Optional - LRU eviction (default)
    use_sql=True,          # Optional - use SQL backend if available
    compress=True,         # Optional - enable compression
    secure=True,           # Optional - secure file permissions
)
def my_function(x: int) -> int:
    return x * x
```

### Smart Backend Selection

Automatically select the best backend based on data characteristics:

```python
from twat_cache import smart_cache

@smart_cache()
def process_data(data_type: str, size: int) -> Any:
    """Process different types of data with automatic backend selection."""
    if data_type == "dict":
        return {f"key_{i}": f"value_{i}" for i in range(size)}
    elif data_type == "list":
        return [i for i in range(size)]
    elif data_type == "str":
        return "x" * size
    else:
        return size
```

### Hybrid Caching

Switch backends based on result size:

```python
from twat_cache import hybrid_cache

@hybrid_cache()
def get_data(size: str) -> Union[Dict[str, Any], List[int]]:
    """Return different sized data with appropriate backend selection."""
    if size == "small":
        # Small result, will use in-memory caching
        return {"name": "Small Data", "value": 42}
    else:
        # Large result, will use disk caching
        return [i for i in range(100000)]
```

### Type-Specific Configuration

Configure caching based on data types:

```python
from twat_cache import ucache, configure_for_numpy, configure_for_json

# For NumPy arrays
@ucache(config=configure_for_numpy())
def process_array(data: np.ndarray) -> np.ndarray:
    return data * 2

# For JSON data
@ucache(config=configure_for_json())
def fetch_json_data(url: str) -> Dict[str, Any]:
    return {"data": [1, 2, 3, 4, 5], "metadata": {"source": url}}
```

### Cache Management

Clear caches and get statistics:

```python
from twat_cache import clear_cache, get_stats

# Clear all caches
clear_cache()

# Get cache statistics
stats = get_stats()
print(stats)  # Shows hits, misses, size, etc.
```

### Context Management

Use cache engines with context management:

```python
from twat_cache import CacheContext, engine_context

# Method 1: Using the CacheContext class
with CacheContext(engine_name="diskcache", folder_name="cache") as cache:
    # Use the cache
    cache.set("key", "value")
    value = cache.get("key")
    
# Method 2: Using the engine_context function
with engine_context(engine_name="redis", ttl=3600) as cache:
    # Use the cache
    cache.set("key", "value")
    value = cache.get("key")
    
# Cache is automatically closed when exiting the context
```

## Advanced Features

### TTL Support

Set time-to-live for cache entries:

```python
from twat_cache import ucache

@ucache(ttl=3600)  # Entries expire after 1 hour
def get_weather(city: str) -> dict:
    # Fetch weather data
    return {"temp": 20}
```

### Eviction Policies

Choose from different cache eviction policies:

```python
from twat_cache import ucache

# Least Recently Used (default)
@ucache(policy="lru")
def function1(x: int) -> int:
    return x * x

# Least Frequently Used
@ucache(policy="lfu")
def function2(x: int) -> int:
    return x * x

# First In, First Out
@ucache(policy="fifo")
def function3(x: int) -> int:
    return x * x
```

## Documentation

For more detailed documentation, see the following resources:

- [Context Management](docs/context_management.md)
- [Backend Selection](docs/backend_selection.md)
- [Cache Engines](docs/cache_engines.md)
- [Configuration Options](docs/configuration.md)
- [API Reference](docs/api_reference.md)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Rationale

Python provides several powerful caching libraries to help optimize application performance by storing and reusing expensive function results. Let's take an in-depth look at some of the most popular options, comparing their features, backends, methods, and use cases.


### Built-in functools 

Python's standard library offers basic caching functionality through the `functools` module. It provides decorators like `@lru_cache(maxsize, typed)` for simple memoization with a Least Recently Used (LRU) eviction policy. The `@cache` decorator is also available, which is equivalent to an unbounded LRU cache.

- **Backend**: In-memory Python dictionary 
- **Eviction Policy**: LRU or unbounded
- **Concurrency**: Thread-safe via internal locks, but not safe for multi-process use
- **Persistence**: No persistence, cache only exists in memory for the lifetime of the process
- **Best For**: Fast and easy caching of function results in memory with minimal setup

```pyi
### functools.pyi (Partial - Caching related parts)

import typing

_T = typing.TypeVar("_T")

@typing.overload
def lru_cache(maxsize: int | None) -> typing.Callable[[_F], _F]: ...
@typing.overload
def lru_cache(maxsize: int | None, typed: bool) -> typing.Callable[[_F], _F]: ...

class _lru_cache_wrapper(typing.Generic[_F]):
    cache: typing.Dict[typing.Tuple[typing.Any, ...], typing.Any]
    def cache_info(self) -> CacheInfo: ...
    def cache_clear(self) -> None: ...
```

```python
import functools

@functools.lru_cache(maxsize=128)
def expensive_function(x):
    return x * 2
```

### cachetools

The `cachetools` library extends the capabilities of `functools` by offering additional cache classes with various eviction policies like LFU, FIFO, TTL, and RR. It also provides `@cached` and `@cachedmethod` decorators for caching functions and methods.

- **Backend**: In-memory Python dictionary
- **Eviction Policies**: LRU, LFU, TTL, FIFO, RR, TLRU 
- **Concurrency**: Thread-safe, not designed for multi-process use
- **Persistence**: In-memory only, no persistence 
- **Customization**: Configurable `maxsize`, `ttl`, custom `getsizeof` to determine item size
- **Best For**: In-memory caching with specific eviction behavior, e.g. caching web API responses

```pyi
### cachetools.pyi (Partial - Most important classes and decorators)

import typing
from typing import Callable

KT = typing.TypeVar("KT")
VT = typing.TypeVar("VT")
DT = typing.TypeVar("DT")

class Cache(typing.MutableMapping[KT, VT]):
    def __init__(self, maxsize: int, getsizeof: Callable[[VT], int] | None = ...) -> None: ...
    @property
    def maxsize(self) -> int: ...
    @property
    def currsize(self) -> int: ...
    def get(self, key: KT, default: DT = ...) -> VT | DT: ...
    def pop(self, key: KT, default: DT = ...) -> VT | DT: ...
    def setdefault(self, key: KT, default: DT = ...) -> VT | DT: ...
    def clear(self) -> None: ...
    @staticmethod
    def getsizeof(value: Any) -> int: ...

class LRUCache(Cache[KT, VT]):
    def __init__(self, maxsize: int, getsizeof: Callable[[VT], int] | None = ...) -> None: ...
    def popitem(self) -> tuple[KT, VT]: ...

class LFUCache(Cache[KT, VT]):
    def __init__(self, maxsize: int, getsizeof: Callable[[VT], int] | None = ...) -> None: ...
    def popitem(self) -> tuple[KT, VT]: ...

class TTLCache(LRUCache[KT, VT]):
    def __init__(self, maxsize: int, ttl: int, timer: Callable[[], float] | None = ..., getsizeof: Callable[[VT], int] | None = ...) -> None: ...
    @property
    def ttl(self) -> int: ...
    def expire(self, time: float | None = ...) -> list[tuple[KT, VT]]: ...
    def popitem(self) -> tuple[KT, VT]: ...

class _CacheInfo(NamedTuple):
    hits: int
    misses: int
    maxsize: int
    currsize: int

_KeyFunc = Callable[..., typing.Hashable]
_Cache = TypeVar("_Cache", bound=Cache)

@overload
def cached(
    cache: _Cache,
    key: _KeyFunc = ...,
    lock: Any | None = ...,
    info: Literal[False] = ...,
) -> Callable[[_F], _F]: ...
@overload
def cached(
    cache: _Cache,
    key: _KeyFunc = ...,
    lock: Any | None = ...,
    info: Literal[True] = ...,
) -> Callable[[_F], _F]: ...

@overload
def cachedmethod(
    cache: Callable[[Any], _Cache],
    key: _KeyFunc = ...,
    lock: Callable[[Any], Any] | None = ...,
) -> Callable[[_F], _F]: ...
@overload
def cachedmethod(
    cache: Callable[[Any], _Cache],
    key: _KeyFunc = ...,
    lock: None = ...,
) -> Callable[[_F], _F]: ...
```

### cachebox

`cachebox` is an in-memory caching solution accelerated by a Rust backend for enhanced performance. It supports similar eviction policies as `cachetools` including a unique variable TTL cache.

- **Backend**: Rust-backed in-memory store
- **Eviction Policies**: LRU, LFU, FIFO, TTL, RR, variable TTL
- **Concurrency**: Thread-safe Rust implementation, but in-memory only
- **Decorators**: `@cached`, `@cachedmethod` support custom key generation and callbacks
- **Best For**: Performant in-memory caching with ample policy choices

```pyi
### cachebox.pyi (Partial - Most important classes)

import typing

KT = typing.TypeVar("KT")
VT = typing.TypeVar("VT")
DT = typing.TypeVar("DT")


class BaseCacheImpl(Generic[KT, VT]):

    def __init__(
        self,
        maxsize: int,
        iterable: Union[Iterable[Tuple[KT, VT]], Dict[KT, VT]] = ...,
        *,
        capacity: int = ...,
    ) -> None: ...
    @property
    def maxsize(self) -> int: ...
    def __len__(self) -> int: ...
    def __contains__(self, key: KT) -> bool: ...
    def __setitem__(self, key: KT, value: VT) -> None: ...
    def __getitem__(self, key: KT) -> VT: ...
    def __delitem__(self, key: KT) -> VT: ...
    def __iter__(self) -> typing.Iterator[KT]: ...
    def capacity(self) -> int: ...
    def is_full(self) -> bool: ...
    def is_empty(self) -> bool: ...
    def insert(self, key: KT, value: VT) -> typing.Optional[VT]: ...
    def get(self, key: KT, default: DT = None) -> typing.Union[VT, DT]: ...
    def pop(self, key: KT, default: DT = None) -> typing.Union[VT, DT]: ...
    def setdefault(
        self, key: KT, default: typing.Optional[DT] = None
    ) -> typing.Optional[VT | DT]: ...
    def popitem(self) -> typing.Tuple[KT, VT]: ...
    def drain(self, n: int) -> int: ...
    def clear(self, *, reuse: bool = False) -> None: ...
    def shrink_to_fit(self) -> None: ...
    def update(
        self, iterable: typing.Union[typing.Iterable[typing.Tuple[KT, VT]], typing.Dict[KT, VT]]
    ) -> None: ...
    def keys(self) -> typing.Iterable[KT]: ...
    def values(self) -> typing.Iterable[VT]: ...
    def items(self) -> typing.Iterable[typing.Tuple[KT, VT]]: ...

class Cache(BaseCacheImpl[KT, VT]):
    def __init__(
        self,
        maxsize: int,
        iterable: Union[Iterable[Tuple[KT, VT]], Dict[KT, VT]] = ...,
        *,
        capacity: int = ...,
    ) -> None:
        ...
    def popitem(self) -> typing.NoReturn: ...  # not implemented for this class
    def drain(self, n: int) -> typing.NoReturn: ...  # not implemented for this class


class FIFOCache(BaseCacheImpl[KT, VT]):
    def __init__(
        self,
        maxsize: int,
        iterable: Union[Iterable[Tuple[KT, VT]], Dict[KT, VT]] = ...,
        *,
        capacity: int = ...,
    ) -> None:
        ...

class RRCache(BaseCacheImpl[KT, VT]):
    def __init__(
        self,
        maxsize: int,
        iterable: Union[Iterable[Tuple[KT, VT]], Dict[KT, VT]] = ...,
        *,
        capacity: int = ...,
    ) -> None:
        ...

class TTLCache(BaseCacheImpl[KT, VT]):
    def __init__(
        self,
        maxsize: int,
        ttl: float,
        iterable: Union[Iterable[Tuple[KT, VT]], Dict[KT, VT]] = ...,
        *,
        capacity: int = ...,
    ) -> None:
        ...

class LRUCache(BaseCacheImpl[KT, VT]):
    def __init__(
        self,
        maxsize: int,
        iterable: Union[Iterable[Tuple[KT, VT]], Dict[KT, VT]] = ...,
        *,
        capacity: int = ...,
    ) -> None:
        ...

class LFUCache(BaseCacheImpl[KT, VT]):
    def __init__(
        self,
        maxsize: int,
        iterable: Union[Iterable[Tuple[KT, VT]], Dict[KT, VT]] = ...,
        *,
        capacity: int = ...,
    ) -> None:
        ...

class VTTLCache(BaseCacheImpl[KT, VT]):
    def __init__(
        self,
        maxsize: int,
        iterable: Union[Iterable[Tuple[KT, VT]], Dict[KT, VT]] = ...,
        ttl: Optional[float] = 0.0,
        *,
        capacity: int = ...,
    ) -> None:
        ...

_CacheType = TypeVar("_CacheType", bound=BaseCacheImpl)

def cached(cache: typing.Optional[_CacheType], key_maker: typing.Optional[Callable[[tuple, dict], typing.Hashable]] = ..., clear_reuse: bool = ..., callback: typing.Optional[Callable[[int, typing.Any, typing.Any], typing.Any]] = ..., copy_level: int = ..., always_copy: typing.Optional[bool] = ...) -> Callable[[_F], _F]: ...
def cachedmethod(cache: typing.Optional[_CacheType], key_maker: typing.Optional[Callable[[tuple, dict], typing.Hashable]] = ..., clear_reuse: bool = ..., callback: typing.Optional[Callable[[int, typing.Any, typing.Any], typing.Any]] = ..., copy_level: int = ..., always_copy: typing.Optional[bool] = ...) -> Callable[[_F], _F]: ...
```

### klepto

For advanced caching workflows, `klepto` provides a highly flexible solution supporting both in-memory and persistent backends like file archives, SQL databases, and HDF5 files. It allows customizing how cache keys are generated and extends the standard cache eviction policies.

- **Backends**: In-memory dict, file archives, SQL databases, HDF5 files
- **Eviction Policies**: Same as `functools` plus LFU, MRU, RR
- **Key Mapping**: `hashmap`, `stringmap`, `picklemap` algorithms to generate keys
- **Persistence**: Archives cache to disk or database for long-term storage
- **Concurrency**: Locking for thread-safety, some process-safety depending on backend
- **Best For**: Complex scenarios needing transient and persistent caching

```pyi
### key maps
class keymap:
    def __init__(self, typed: bool = False, flat: bool = True,
                 sentinel: object=...) -> None: ...
    def __call__(self, *args, **kwargs) -> object: ...

class hashmap(keymap):
    def __init__(self, algorithm: Optional[str] = None,
                 typed: bool = False, flat: bool = True,
                 sentinel: object=...) -> None: ...

class stringmap(keymap):
    def __init__(self, encoding: Optional[str] = None,
                 typed: bool = False, flat: bool = True,
                 sentinel: object=...) -> None: ...

class picklemap(keymap):
    def __init__(self, serializer: Optional[str] = None,
                 typed: bool = False, flat: bool = True,
                 sentinel: object=...) -> None: ...

### base archive
class archive(dict):
    def __init__(self, *args, **kwds) -> None: ...
    def __asdict__(self) -> dict: ...
    def __repr__(self) -> str: ...
    def copy(self, name: Optional[str] = None) -> 'archive': ...
    def load(self, *args) -> None: ...
    def dump(self, *args) -> None: ...
    def archived(self, *on) -> bool: ...
    def sync(self, clear: bool = False) -> None: ...
    def drop(self) -> None: ...
    def open(self, archive: 'archive') -> None: ...

    @property
    def archive(self) -> 'archive': ...
    @archive.setter
    def archive(self, archive: 'archive') -> None: ...
    @property
    def name(self) -> str: ...
    @name.setter
    def name(self, archive: 'archive') -> None: ...
    @property
    def state(self) -> dict: ...
    @state.setter
    def state(self, archive: 'archive') -> None: ...

class dict_archive(archive):
    def __init__(self, *args, **kwds) -> None: ...

class null_archive(archive):
    def __init__(self, *args, **kwds) -> None: ...

class file_archive(archive):
    def __init__(self, filename: Optional[str] = None, dict: Optional[dict] = None,
                 cached: bool = True, serialized: bool = True,
                 protocol: Optional[int] = None, *args, **kwds) -> None: ...

class dir_archive(archive):
    def __init__(self, dirname: Optional[str] = None, dict: Optional[dict] = None,
                 cached: bool = True, serialized: bool = True,
                 compression: int = 0, permissions: Optional[int] = None,
                 memmode: Optional[str] = None, memsize: int = 100,
                 protocol: Optional[int] = None, *args, **kwds) -> None: ...

class sqltable_archive(archive):
    def __init__(self, database: Optional[str] = None,
                 table: Optional[str] = None, dict: Optional[dict] = None,
                 cached: bool = True, serialized: bool = True,
                 protocol: Optional[int] = None, *args, **kwds) -> None: ...

class sql_archive(archive):
    def __init__(self, database: Optional[str] = None, dict: Optional[dict] = None,
                 cached: bool = True, serialized: bool = True,
                 protocol: Optional[int] = None, *args, **kwds) -> None: ...

class hdfdir_archive(archive):
    def __init__(self, dirname: Optional[str] = None, dict: Optional[dict] = None,
                 cached: bool = True, serialized: bool = True,
                 permissions: Optional[int] = None,
                 protocol: Optional[int] = None, *args, **kwds) -> None: ...

class hdf_archive(archive):
    def __init__(self, filename: Optional[str] = None, dict: Optional[dict] = None,
                 cached: bool = True, serialized: bool = True,
                 protocol: Optional[int] = None, *args, **kwds) -> None: ...
```

### diskcache

When caching large datasets that should survive process restarts, `diskcache` shines with its optimized disk-backed storage using SQLite and the filesystem. It offers a range of eviction policies, a sharded `FanoutCache`, and persistent data structures like `Deque` and `Index`.

- **Backend**: SQLite for metadata, filesystem for data
- **Eviction Policies**: Configurable, including LRU and LFU
- **Persistence**: Data persists on disk between process runs
- **Concurrency**: Thread and process-safe 
- **Added Features**: Stampede prevention, throttling, optimized I/O
- **Best For**: Persistent caching for web apps and data pipelines

```pyi
### diskcache.pyi (Partial - Most important classes)

import typing
from typing import Callable, List, Dict, Any, IO, Optional, Tuple, Union

class Cache:
    def __init__(self, directory: Optional[str] = ..., timeout: float = ..., disk: Type[Disk] = ..., **settings: Any) -> None: ...
    @property
    def directory(self) -> str: ...
    @property
    def timeout(self) -> float: ...
    @property
    def disk(self) -> Disk: ...
    def set(self, key: Any, value: Any, expire: Optional[float] = ..., read: bool = ..., tag: Optional[str] = ..., retry: bool = ...) -> bool: ...
    def get(self, key: Any, default: Optional[Any] = ..., read: bool = ..., expire_time: bool = ..., tag: bool = ..., retry: bool = ...) -> Any: ...
    def delete(self, key: Any, retry: bool = ...) -> bool: ...
    def clear(self, retry: bool = ...) -> int: ...
    def volume(self) -> int: ...
    def check(self, fix: bool = ..., retry: bool = ...) -> List[warnings.WarningMessage]: ...
    def transact(self, retry: bool = ...) -> ContextManager[Callable]: ...
    def memoize(self, name: Optional[str] = ..., typed: bool = ..., expire: Optional[float] = ..., tag: Optional[str] = ..., ignore: typing.Iterable[str] = ...) -> Callable[[_F], _F]: ...
    def close(self) -> None: ...
    def volume(self) -> int: ...
    def stats(self, enable: bool = ..., reset: bool = ...) -> Tuple[int, int]: ...
    def volume(self) -> int: ...

class FanoutCache:
    def __init__(self, directory: Optional[str] = ..., shards: int = ..., timeout: float = ..., disk: Type[Disk] = ..., **settings: Any) -> None: ...
    @property
    def directory(self) -> str: ...
    def transact(self, retry: bool = ...) -> ContextManager[Callable]: ...
    def set(self, key: Any, value: Any, expire: Optional[float] = ..., read: bool = ..., tag: Optional[str] = ..., retry: bool = ...) -> bool: ...
    def get(self, key: Any, default: Optional[Any] = ..., read: bool = ..., expire_time: bool = ..., tag: bool = ..., retry: bool = ...) -> Any: ...
    def delete(self, key: Any, retry: bool = ...) -> bool: ...
    def clear(self, retry: bool = ...) -> int: ...
    def volume(self) -> int: ...
    def stats(self, enable: bool = ..., reset: bool = ...) -> Tuple[int, int]: ...
    def memoize(self, name: Optional[str] = ..., typed: bool = ..., expire: Optional[float] = ..., tag: Optional[str] = ..., ignore: typing.Iterable[str] = ...) -> Callable[[_F], _F]: ...
    def close(self) -> None: ...
    def volume(self) -> int: ...

class Disk:
    def __init__(self, directory: str, min_file_size: int = ..., pickle_protocol: int = ...) -> None: ...
    @property
    def min_file_size(self) -> int: ...
    @property
    def pickle_protocol(self) -> int: ...
    def put(self, key: Any) -> Tuple[Union[str, sqlite3.Binary, int, float], bool]: ...
    def get(self, key: Union[str, sqlite3.Binary, int, float], raw: bool) -> Any: ...
    def store(self, value: Any, read: bool, key: Constant = ...) -> Tuple[int, int, Optional[str], Optional[Union[str, sqlite3.Binary, int, float]]]: ...
    def fetch(self, mode: int, filename: Optional[str], value: Optional[Union[str, sqlite3.Binary, int, float]], read: bool) -> Any: ...

class JSONDisk(Disk):
    def __init__(self, directory: str, compress_level: int = ..., **kwargs: Any) -> None: ...
```

### joblib

Designed for scientific computing and ML workflows, `joblib` offers transparent disk-caching for functions, with optimizations for large NumPy arrays. Results are saved to disk and only re-computed when inputs change.

- **Backend**: Filesystem
- **Persistence**: Caches results to disk for costly computations
- **Memoization**: `@memory.cache` decorator for functions
- **Serialization**: Pickle-based with optional compression
- **Concurrency**: Process-safe file locking
- **Best For**: Caching ML models, features, large NumPy arrays

```pyi
### joblib.pyi (Partial - Most important classes and functions)

import typing
from typing import Callable, List, Dict, Any, IO, Optional, Tuple, Union

_F = TypeVar("_F", bound=Callable[..., Any])

class Memory:
    def __init__(self, location: Optional[str] = ..., backend: str = ..., verbose: int = ..., bytes_limit: Optional[Union[int, str]] = ..., mmap_mode: Optional[str] = ..., compress: Union[bool, int] = ..., backend_options: Optional[Dict[str, Any]] = ...) -> None: ...
    @property
    def location(self) -> str: ...
    @property
    def backend(self) -> str: ...
    @property
    def compress(self) -> Union[bool, int]: ...
    @property
    def verbose(self) -> int: ...
    def cache(self, func: Optional[_F] = ..., ignore: Optional[List[str]] = ..., verbose: Optional[int] = ..., mmap_mode: Optional[str] = ..., cache_validation_callback: Optional[Callable[[Dict[str, Any]], bool]] = ...) -> _F: ...
    def clear(self, warn: bool = ...) -> None: ...
    def eval(self, func: _F, *args: Any, **kwargs: Any) -> Any: ...
    def __call__(self, func: _F, *args: Any, **kwargs: Any) -> Any: ...

class Parallel:
    def __init__(self, n_jobs: Optional[int] = ..., backend: Optional[str] = ..., verbose: int = ..., timeout: Optional[float] = ..., pre_dispatch: Union[str, int] = ..., batch_size: Union[str, int] = ..., temp_folder: Optional[str] = ..., max_nbytes: Optional[Union[int, str]] = ..., mmap_mode: Optional[str] = ..., prefer: Optional[str] = ..., require: Optional[str] = ...) -> None: ...
    def __call__(self, iterable: typing.Iterable) -> List[Any]: ...
    def __enter__(self) -> "Parallel": ...
    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_value: Optional[BaseException], traceback: Optional[TracebackType]) -> None: ...
    def submit(self, func: _F, *args: Any, **kwargs: Any) -> concurrent.futures.Future: ...
    def map(self, func: _F, *iterables: typing.Iterable, timeout: Optional[float] = ..., chunksize: int = ...) -> typing.Iterable[Any]: ...
    def dispatch_next(self) -> None: ...
    def print_progress(self) -> None: ...
    def clear(self) -> None: ...
    def __len__(self) -> int: ...

def delayed(function: _F) -> Callable[..., Tuple[Callable, tuple, dict]]: ...
def cpu_count(only_physical_cores: bool = ...) -> int: ...
def effective_n_jobs(n_jobs: int = ...) -> int: ...
def hash(obj: Any, hash_name: str = ..., coerce_mmap: bool = ...) -> str: ...
def dump(value: Any, filename: Union[str, PathLikeStr], compress: Union[bool, int] = ..., protocol: Optional[int] = ..., cache_size: Optional[int] = ...) -> List[str]: ...
def load(filename: Union[str, PathLikeStr], mmap_mode: Optional[str] = ...) -> Any: ...
def register_parallel_backend(name: str, factory: Callable[..., ParallelBackendBase], make_default: bool = ...) -> None: ...

#### aiocache

Built for async applications using the `asyncio` framework, `aiocache` enables non-blocking caching operations. It provides both in-memory (`SimpleMemoryCache`) and distributed options (`RedisCache`, `MemcachedCache`).

- **Backends**: In-memory, Redis, Memcached
- **Async Decorators**: `@cached`, `@cached_stampede`, `@multi_cached`  
- **Serialization**: Pluggable, defaults to JSON
- **Best For**: Asynchronous web frameworks (FastAPI, Sanic), distributed caching

```pyi
### aiocache.pyi (Partial - Most important classes and decorators)

import typing
from typing import Any, Callable, Coroutine, Dict, List, Optional, Tuple, Type, Union

_F = typing.TypeVar("_F", bound=Callable[..., Any])

class BaseCache:
    NAME: str
    def __init__(self, serializer: Optional[BaseSerializer] = ..., plugins: Optional[List[BasePlugin]] = ..., namespace: Optional[str] = ..., timeout: float = ..., ttl: Optional[int] = ...) -> None: ...
    @classmethod
    def parse_uri_path(cls, path: str) -> Dict[str, str]: ...
    async def add(self, key: str, value: Any, ttl: Optional[int] = ..., dumps_fn: Optional[Callable[[Any], bytes]] = ..., namespace: Optional[str] = ..., timeout: Optional[int] = ...) -> bool: ...
    async def get(self, key: str, default: Optional[Any] = ..., loads_fn: Optional[Callable[[bytes], Any]] = ..., namespace: Optional[str] = ..., timeout: Optional[int] = ...) -> Any: ...
    async def multi_get(self, keys: List[str], loads_fn: Optional[Callable[[bytes], Any]] = ..., namespace: Optional[str] = ..., timeout: Optional[int] = ...) -> List[Any]: ...
    async def set(self, key: str, value: Any, ttl: Optional[int] = ..., dumps_fn: Optional[Callable[[Any], bytes]] = ..., namespace: Optional[str] = ..., timeout: Optional[int] = ..., _cas_token: Optional[Any] = ...) -> bool: ...
    async def multi_set(self, pairs: List[Tuple[str, Any]], ttl: Optional[int] = ..., dumps_fn: Optional[Callable[[Any], bytes]] = ..., namespace: Optional[str] = ..., timeout: Optional[int] = ...) -> bool: ...
    async def delete(self, key: str, namespace: Optional[str] = ..., timeout: Optional[int] = ...) -> int: ...
    async def exists(self, key: str, namespace: Optional[str] = ..., timeout: Optional[int] = ...) -> bool: ...
    async def increment(self, key: str, delta: int = ..., namespace: Optional[str] = ..., timeout: Optional[int] = ...) -> int: ...
    async def expire(self, key: str, ttl: Optional[int] = ..., namespace: Optional[str] = ..., timeout: Optional[int] = ...) -> bool: ...
    async def clear(self, namespace: Optional[str] = ..., timeout: Optional[int] = ...) -> bool: ...
    async def close(self, timeout: Optional[int] = ...) -> bool: ...
    async def raw(self, command: str, *args: Any, encoding: Optional[str] = ..., timeout: Optional[int] = ..., **kwargs: Any) -> Any: ...

class SimpleMemoryCache(BaseCache):
    NAME: str
    def __init__(self, serializer: Optional[BaseSerializer] = ..., **kwargs: Any) -> None: ...

class RedisCache(BaseCache):
    NAME: str
    def __init__(self, serializer: Optional[BaseSerializer] = ..., **kwargs: Any) -> None: ...

class MemcachedCache(BaseCache):
    NAME: str
    def __init__(self, serializer: Optional[BaseSerializer] = ..., **kwargs: Any) -> None: ...

class BaseSerializer:
    DEFAULT_ENCODING: Optional[str]
    def __init__(self, *args: Any, encoding: Union[str, object] = ..., **kwargs: Any) -> None: ...
    def dumps(self, value: Any) -> bytes: ...
    def loads(self, value: bytes) -> Any: ...

class JsonSerializer(BaseSerializer):
    def dumps(self, value: Any) -> str: ...
    def loads(self, value: str) -> Any: ...

class PickleSerializer(BaseSerializer):
    def dumps(self, value: Any) -> bytes: ...
    def loads(self, value: bytes) -> Any: ...

class NullSerializer(BaseSerializer):
    def dumps(self, value: Any) -> Any: ...
    def loads(self, value: Any) -> Any: ...

class BasePlugin:
    async def pre_get(self, client: BaseCache, key: str, namespace: Optional[str], **kwargs: Any) -> None: ...
    async def post_get(self, client: BaseCache, key: str, namespace: Optional[str], rv: Any, **kwargs: Any) -> None: ...
    # ... (and similar methods for other cache operations)

_Cache = TypeVar("_Cache", bound=BaseCache)

def cached(
    ttl: Optional[int] = ...,
    key: Optional[str] = ...,
    key_builder: Optional[Callable[..., str]] = ...,
    namespace: Optional[str] = ...,
    cache: Union[Type[_Cache], str] = ...,
    serializer: Optional[BaseSerializer] = ...,
    plugins: Optional[List[BasePlugin]] = ...,
    alias: Optional[str] = ...,
    noself: bool = ...,
    skip_cache_func: Optional[Callable[[Any], bool]] = ...,
    **kwargs: Any
) -> Callable[[_F], _F]: ...

def cached_stampede(
    lease: int = ...,
    ttl: Optional[int] = ...,
    key: Optional[str] = ...,
    key_builder: Optional[Callable[..., str]] = ...,
    namespace: Optional[str] = ...,
    cache: Union[Type[_Cache], str] = ...,
    serializer: Optional[BaseSerializer] = ...,
    plugins: Optional[List[BasePlugin]] = ...,
    alias: Optional[str] = ...,
    noself: bool = ...,
    skip_cache_func: Optional[Callable[[Any], bool]] = ...,
    **kwargs: Any
) -> Callable[[_F], _F]: ...

def multi_cached(
    keys_from_attr: Optional[str] = ...,
    namespace: Optional[str] = ...,
    key_builder: Optional[Callable[..., str]] = ...,
    ttl: Optional[int] = ...,
    cache: Union[Type[_Cache], str] = ...,
    serializer: Optional[BaseSerializer] = ...,
    plugins: Optional[List[BasePlugin]] = ...,
    alias: Optional[str] = ...,
    skip_cache_func: Optional[Callable[[str, Any], bool]] = ...,
    **kwargs: Any
) -> Callable[[_F], _F]: ...
```

### Summary of type hints

```pyi
### Type Stubs for Caching Libraries

from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Type,
    Iterable,
    Tuple,
    Union,
    TypeVar,
    Generic,
)
import datetime
import logging
from typing_extensions import Literal  # For older Python versions
```

*   **Generics:** For generic types like `Cache`, `FIFOCache`, `LFUCache`, etc. (in `cachetools`, `cachebox`, `klepto`) , I've used `TypeVar` to represent the key (`KT`) and value (`VT`) types.  This gives better type hinting.
*   **`object` as Default:** Where the original code uses implicit dynamic typing (no explicit type) or uses an internal implementation detail, I've often used `object` as the most general type hint.  This avoids creating stubs for internal classes.
*   **`NotImplementedError` and `typing.NoReturn`:** I've used `typing.NoReturn` for methods that are *not implemented* in a base class.  This is more precise than raising `NotImplementedError`, which would imply that a subclass *should* implement it.
*   **`defaultdict`:**  I've handled cases where `defaultdict` is used internally, providing a default factory function.
*   **`_Conn`:**  This internal helper class from `aiocache` is fully defined as all its methods are based on exported API.
* **`_DISTUTILS_PATCH`, `VIRTUALENV_PATCH_FILE`, etc.:** These internal constants/classes, used for patching `distutils`, are omitted.
*   **`kwargs` Handling:** In many cases, I've used `**kwargs` to represent arbitrary keyword arguments, especially when those arguments are passed directly to another function (like `open` or a backend-specific constructor).
* **`functools`:** The return type of decorators (`lru_cache`, `cache`) is `Callable[[Callable[..., R]], Callable[..., R]]`.  I've used a `TypeVar` named `_R` to make the relationship between the input and output types clear.
* **`klepto` classes**: Added the API for the `archive`, `dir_archive`, `sql_archive`, `sqltable_archive` based on the source code.
* **`joblib` classes**: Added the classes in the public API, `Memory`, `MemorizedFunc`, `NotMemorizedFunc`.

#### Recommendations

The best caching library depends on your specific needs - whether you require persistence, have large datasets, need multi-process safety, or are using an async framework. By understanding the strengths of each library, you can make an informed choice to optimize your application's performance.


---

_**Assistant**_

<think>The user wants me to incorporate caching features into the opero package we've been discussing, inspired by the twat-cache library they shared. Let me analyze what this entails:

1. The user has provided a detailed description of the twat-cache library, which is a flexible caching utility for Python functions
2. They want similar functionality incorporated into the opero API rewrite we've been planning
3. I need to develop a plan that includes caching alongside the existing retry and fallback mechanisms

First, let's understand what the twat-cache library offers:
- Multiple decorators for different caching needs (mcache, bcache, ucache, etc.)
- Support for various backends (memory, disk, Redis, etc.)
- TTL (time-to-live) support
- Eviction policies (LRU, LFU, FIFO)
- Context management for caches
- Smart backend selection based on data types

Now, I need to think about how to incorporate these features into the opero API alongside the existing retry and fallback mechanisms.</think># Enhanced Opero API Plan with Caching Support

Based on your request, I've designed a comprehensive plan to incorporate caching capabilities into the `opero` package, inspired by `twat-cache`. This adds powerful caching alongside the resilience features we've already planned.

Let me update the implementation plan with caching support:

---

_****_



---

_****_



---

_**User**_

try again

---

_**Assistant**_

I'll update the TODO.md file to incorporate caching capabilities into the opero package, inspired by the twat-cache library.

---

_****_



---

_****_



---

_**User**_

Incorporate caching as well, using twat-cache. Make the code depend directly on twat-mp (for concurrency/multiprocessing) and twat-cache (for caching). 


We have concurrency/multiprocessing, we have rate limiting, we have retrying, we have fallback, and we have caching. Order these functionalities logically, so that the implementation that exposes all of these functionalities makes sense. 




===


# twat-cache

A flexible caching utility package for Python functions that provides a unified interface for caching function results using various high-performance backends.

## Features

- Simple decorator interface for caching function results
- Multiple caching backends with automatic selection:
  1. `cachebox` - Very fast Rust-based cache (optional)
  2. `cachetools` - Flexible in-memory caching (optional)
  3. `aiocache` - Async-capable caching (optional)
  4. `klepto` - Scientific computing caching (optional)
  5. `diskcache` - SQL-based disk cache (optional)
  6. `joblib` - Efficient array caching (optional)
  7. `redis` - Distributed caching with Redis (optional)
  8. Memory-based LRU cache (always available)
- Automatic cache directory management
- Type hints and modern Python features
- Lazy backend loading - only imports what you use
- Automatic backend selection based on availability and use case
- Smart backend selection based on data characteristics
- TTL support for cache expiration
- Multiple eviction policies (LRU, LFU, FIFO, RR)
- Async function support
- Compression options for large data
- Secure file permissions for sensitive data
- Hybrid caching with automatic backend switching
- Context management for cache engines
- Comprehensive test suite for all components

## Recent Updates (v2.3.0)

### Enhanced Context Management

The context management system has been significantly improved:
- Better error handling and resource cleanup
- Support for explicit engine selection
- Simplified API for temporary cache configurations
- Automatic cleanup of resources even when exceptions occur

```python
# Example of improved context management
from twat_cache import CacheContext

# Create a context with explicit engine selection
with CacheContext(engine_name="redis", namespace="user_data") as cache:
    # Use the cache within the context
    cache.set("user:1001", {"name": "John", "role": "admin"})
    user = cache.get("user:1001")
    
    # Resources are automatically cleaned up when exiting the context
```

### Refined Backend Selection

The backend selection strategy has been further enhanced:
- More accurate data type detection for optimal backend selection
- Improved fallback mechanisms when preferred backends are unavailable
- Better handling of edge cases for various data types
- Enhanced performance for frequently accessed items

### Comprehensive Documentation

Documentation has been expanded with:
- Detailed examples for all cache backends
- Step-by-step guides for common use cases
- API reference with complete parameter descriptions
- Best practices for cache configuration

## Installation

Basic installation with just LRU caching:
```bash
pip install twat-cache
```

With all optional backends:
```bash
pip install twat-cache[all]
```

Or install specific backends:
```bash
pip install twat-cache[cachebox]     # For Rust-based high-performance cache
pip install twat-cache[cachetools]   # For flexible in-memory caching
pip install twat-cache[aiocache]     # For async-capable caching
pip install twat-cache[klepto]       # For scientific computing caching
pip install twat-cache[diskcache]    # For SQL-based disk caching
pip install twat-cache[joblib]       # For efficient array caching
pip install twat-cache[redis]        # For distributed caching with Redis
```

## Usage

### Basic Memory Caching

For simple in-memory caching with LRU eviction:

```python
from twat_cache import mcache

@mcache(maxsize=100)  # Cache up to 100 items
def expensive_function(x: int) -> int:
    # Expensive computation here
    return x * x

# First call computes
result1 = expensive_function(5)  # Computes 25

# Second call uses cache
result2 = expensive_function(5)  # Returns cached 25
```

### Disk-Based Caching

For persistent caching using SQLite:

```python
from twat_cache import bcache

@bcache(
    folder_name="my_cache",  # Cache directory name
    maxsize=1_000_000,       # Max cache size in bytes
    ttl=3600,               # Cache entries expire after 1 hour
    use_sql=True,           # Use SQLite backend
    secure=True,            # Use secure file permissions
)
def expensive_function(x: int) -> int:
    return x * x
```

### Redis Distributed Caching

For distributed caching with Redis:

```python
from twat_cache import ucache

@ucache(
    preferred_engine="redis",
    folder_name="redis_cache",  # Used as Redis namespace
    ttl=3600,                  # Cache entries expire after 1 hour
    compress=True,             # Enable compression
)
def expensive_function(x: int) -> int:
    return x * x
```

### File-Based Caching

For efficient caching of large objects like NumPy arrays:

```python
from twat_cache import fcache
import numpy as np

@fcache(
    folder_name="array_cache",
    compress=True,           # Enable compression
    secure=True,            # Use secure file permissions
)
def process_array(data: np.ndarray) -> np.ndarray:
    # Expensive array processing here
    return data * 2
```

### Async Caching

For async functions with Redis or memory backend:

```python
from twat_cache import ucache

@ucache(use_async=True)
async def fetch_data(url: str) -> dict:
    # Async web request here
    return {"data": "..."}

# First call fetches
data1 = await fetch_data("https://api.example.com")

# Second call uses cache
data2 = await fetch_data("https://api.example.com")
```

### Universal Caching

Let the library choose the best backend:

```python
from twat_cache import ucache

@ucache(
    folder_name="cache",     # Optional - uses disk cache if provided
    maxsize=1000,           # Optional - limits cache size
    ttl=3600,              # Optional - entries expire after 1 hour
    policy="lru",          # Optional - LRU eviction (default)
    use_sql=True,          # Optional - use SQL backend if available
    compress=True,         # Optional - enable compression
    secure=True,           # Optional - secure file permissions
)
def my_function(x: int) -> int:
    return x * x
```

### Smart Backend Selection

Automatically select the best backend based on data characteristics:

```python
from twat_cache import smart_cache

@smart_cache()
def process_data(data_type: str, size: int) -> Any:
    """Process different types of data with automatic backend selection."""
    if data_type == "dict":
        return {f"key_{i}": f"value_{i}" for i in range(size)}
    elif data_type == "list":
        return [i for i in range(size)]
    elif data_type == "str":
        return "x" * size
    else:
        return size
```

### Hybrid Caching

Switch backends based on result size:

```python
from twat_cache import hybrid_cache

@hybrid_cache()
def get_data(size: str) -> Union[Dict[str, Any], List[int]]:
    """Return different sized data with appropriate backend selection."""
    if size == "small":
        # Small result, will use in-memory caching
        return {"name": "Small Data", "value": 42}
    else:
        # Large result, will use disk caching
        return [i for i in range(100000)]
```

### Type-Specific Configuration

Configure caching based on data types:

```python
from twat_cache import ucache, configure_for_numpy, configure_for_json

# For NumPy arrays
@ucache(config=configure_for_numpy())
def process_array(data: np.ndarray) -> np.ndarray:
    return data * 2

# For JSON data
@ucache(config=configure_for_json())
def fetch_json_data(url: str) -> Dict[str, Any]:
    return {"data": [1, 2, 3, 4, 5], "metadata": {"source": url}}
```

### Cache Management

Clear caches and get statistics:

```python
from twat_cache import clear_cache, get_stats

# Clear all caches
clear_cache()

# Get cache statistics
stats = get_stats()
print(stats)  # Shows hits, misses, size, etc.
```

### Context Management

Use cache engines with context management:

```python
from twat_cache import CacheContext, engine_context

# Method 1: Using the CacheContext class
with CacheContext(engine_name="diskcache", folder_name="cache") as cache:
    # Use the cache
    cache.set("key", "value")
    value = cache.get("key")
    
# Method 2: Using the engine_context function
with engine_context(engine_name="redis", ttl=3600) as cache:
    # Use the cache
    cache.set("key", "value")
    value = cache.get("key")
    
# Cache is automatically closed when exiting the context
```

## Advanced Features

### TTL Support

Set time-to-live for cache entries:

```python
from twat_cache import ucache

@ucache(ttl=3600)  # Entries expire after 1 hour
def get_weather(city: str) -> dict:
    # Fetch weather data
    return {"temp": 20}
```

### Eviction Policies

Choose from different cache eviction policies:

```python
from twat_cache import ucache

# Least Recently Used (default)
@ucache(policy="lru")
def function1(x: int) -> int:
    return x * x

# Least Frequently Used
@ucache(policy="lfu")
def function2(x: int) -> int:
    return x * x

# First In, First Out
@ucache(policy="fifo")
def function3(x: int) -> int:
    return x * x
```

## Documentation

For more detailed documentation, see the following resources:

- [Context Management](docs/context_management.md)
- [Backend Selection](docs/backend_selection.md)
- [Cache Engines](docs/cache_engines.md)
- [Configuration Options](docs/configuration.md)
- [API Reference](docs/api_reference.md)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Rationale

Python provides several powerful caching libraries to help optimize application performance by storing and reusing expensive function results. Let's take an in-depth look at some of the most popular options, comparing their features, backends, methods, and use cases.


### Built-in functools 

Python's standard library offers basic caching functionality through the `functools` module. It provides decorators like `@lru_cache(maxsize, typed)` for simple memoization with a Least Recently Used (LRU) eviction policy. The `@cache` decorator is also available, which is equivalent to an unbounded LRU cache.

- **Backend**: In-memory Python dictionary 
- **Eviction Policy**: LRU or unbounded
- **Concurrency**: Thread-safe via internal locks, but not safe for multi-process use
- **Persistence**: No persistence, cache only exists in memory for the lifetime of the process
- **Best For**: Fast and easy caching of function results in memory with minimal setup

```pyi
### functools.pyi (Partial - Caching related parts)

import typing

_T = typing.TypeVar("_T")

@typing.overload
def lru_cache(maxsize: int | None) -> typing.Callable[[_F], _F]: ...
@typing.overload
def lru_cache(maxsize: int | None, typed: bool) -> typing.Callable[[_F], _F]: ...

class _lru_cache_wrapper(typing.Generic[_F]):
    cache: typing.Dict[typing.Tuple[typing.Any, ...], typing.Any]
    def cache_info(self) -> CacheInfo: ...
    def cache_clear(self) -> None: ...
```

```python
import functools

@functools.lru_cache(maxsize=128)
def expensive_function(x):
    return x * 2
```

### cachetools

The `cachetools` library extends the capabilities of `functools` by offering additional cache classes with various eviction policies like LFU, FIFO, TTL, and RR. It also provides `@cached` and `@cachedmethod` decorators for caching functions and methods.

- **Backend**: In-memory Python dictionary
- **Eviction Policies**: LRU, LFU, TTL, FIFO, RR, TLRU 
- **Concurrency**: Thread-safe, not designed for multi-process use
- **Persistence**: In-memory only, no persistence 
- **Customization**: Configurable `maxsize`, `ttl`, custom `getsizeof` to determine item size
- **Best For**: In-memory caching with specific eviction behavior, e.g. caching web API responses

```pyi
### cachetools.pyi (Partial - Most important classes and decorators)

import typing
from typing import Callable

KT = typing.TypeVar("KT")
VT = typing.TypeVar("VT")
DT = typing.TypeVar("DT")

class Cache(typing.MutableMapping[KT, VT]):
    def __init__(self, maxsize: int, getsizeof: Callable[[VT], int] | None = ...) -> None: ...
    @property
    def maxsize(self) -> int: ...
    @property
    def currsize(self) -> int: ...
    def get(self, key: KT, default: DT = ...) -> VT | DT: ...
    def pop(self, key: KT, default: DT = ...) -> VT | DT: ...
    def setdefault(self, key: KT, default: DT = ...) -> VT | DT: ...
    def clear(self) -> None: ...
    @staticmethod
    def getsizeof(value: Any) -> int: ...

class LRUCache(Cache[KT, VT]):
    def __init__(self, maxsize: int, getsizeof: Callable[[VT], int] | None = ...) -> None: ...
    def popitem(self) -> tuple[KT, VT]: ...

class LFUCache(Cache[KT, VT]):
    def __init__(self, maxsize: int, getsizeof: Callable[[VT], int] | None = ...) -> None: ...
    def popitem(self) -> tuple[KT, VT]: ...

class TTLCache(LRUCache[KT, VT]):
    def __init__(self, maxsize: int, ttl: int, timer: Callable[[], float] | None = ..., getsizeof: Callable[[VT], int] | None = ...) -> None: ...
    @property
    def ttl(self) -> int: ...
    def expire(self, time: float | None = ...) -> list[tuple[KT, VT]]: ...
    def popitem(self) -> tuple[KT, VT]: ...

class _CacheInfo(NamedTuple):
    hits: int
    misses: int
    maxsize: int
    currsize: int

_KeyFunc = Callable[..., typing.Hashable]
_Cache = TypeVar("_Cache", bound=Cache)

@overload
def cached(
    cache: _Cache,
    key: _KeyFunc = ...,
    lock: Any | None = ...,
    info: Literal[False] = ...,
) -> Callable[[_F], _F]: ...
@overload
def cached(
    cache: _Cache,
    key: _KeyFunc = ...,
    lock: Any | None = ...,
    info: Literal[True] = ...,
) -> Callable[[_F], _F]: ...

@overload
def cachedmethod(
    cache: Callable[[Any], _Cache],
    key: _KeyFunc = ...,
    lock: Callable[[Any], Any] | None = ...,
) -> Callable[[_F], _F]: ...
@overload
def cachedmethod(
    cache: Callable[[Any], _Cache],
    key: _KeyFunc = ...,
    lock: None = ...,
) -> Callable[[_F], _F]: ...
```

### cachebox

`cachebox` is an in-memory caching solution accelerated by a Rust backend for enhanced performance. It supports similar eviction policies as `cachetools` including a unique variable TTL cache.

- **Backend**: Rust-backed in-memory store
- **Eviction Policies**: LRU, LFU, FIFO, TTL, RR, variable TTL
- **Concurrency**: Thread-safe Rust implementation, but in-memory only
- **Decorators**: `@cached`, `@cachedmethod` support custom key generation and callbacks
- **Best For**: Performant in-memory caching with ample policy choices

```pyi
### cachebox.pyi (Partial - Most important classes)

import typing

KT = typing.TypeVar("KT")
VT = typing.TypeVar("VT")
DT = typing.TypeVar("DT")


class BaseCacheImpl(Generic[KT, VT]):

    def __init__(
        self,
        maxsize: int,
        iterable: Union[Iterable[Tuple[KT, VT]], Dict[KT, VT]] = ...,
        *,
        capacity: int = ...,
    ) -> None: ...
    @property
    def maxsize(self) -> int: ...
    def __len__(self) -> int: ...
    def __contains__(self, key: KT) -> bool: ...
    def __setitem__(self, key: KT, value: VT) -> None: ...
    def __getitem__(self, key: KT) -> VT: ...
    def __delitem__(self, key: KT) -> VT: ...
    def __iter__(self) -> typing.Iterator[KT]: ...
    def capacity(self) -> int: ...
    def is_full(self) -> bool: ...
    def is_empty(self) -> bool: ...
    def insert(self, key: KT, value: VT) -> typing.Optional[VT]: ...
    def get(self, key: KT, default: DT = None) -> typing.Union[VT, DT]: ...
    def pop(self, key: KT, default: DT = None) -> typing.Union[VT, DT]: ...
    def setdefault(
        self, key: KT, default: typing.Optional[DT] = None
    ) -> typing.Optional[VT | DT]: ...
    def popitem(self) -> typing.Tuple[KT, VT]: ...
    def drain(self, n: int) -> int: ...
    def clear(self, *, reuse: bool = False) -> None: ...
    def shrink_to_fit(self) -> None: ...
    def update(
        self, iterable: typing.Union[typing.Iterable[typing.Tuple[KT, VT]], typing.Dict[KT, VT]]
    ) -> None: ...
    def keys(self) -> typing.Iterable[KT]: ...
    def values(self) -> typing.Iterable[VT]: ...
    def items(self) -> typing.Iterable[typing.Tuple[KT, VT]]: ...

class Cache(BaseCacheImpl[KT, VT]):
    def __init__(
        self,
        maxsize: int,
        iterable: Union[Iterable[Tuple[KT, VT]], Dict[KT, VT]] = ...,
        *,
        capacity: int = ...,
    ) -> None:
        ...
    def popitem(self) -> typing.NoReturn: ...  # not implemented for this class
    def drain(self, n: int) -> typing.NoReturn: ...  # not implemented for this class


class FIFOCache(BaseCacheImpl[KT, VT]):
    def __init__(
        self,
        maxsize: int,
        iterable: Union[Iterable[Tuple[KT, VT]], Dict[KT, VT]] = ...,
        *,
        capacity: int = ...,
    ) -> None:
        ...

class RRCache(BaseCacheImpl[KT, VT]):
    def __init__(
        self,
        maxsize: int,
        iterable: Union[Iterable[Tuple[KT, VT]], Dict[KT, VT]] = ...,
        *,
        capacity: int = ...,
    ) -> None:
        ...

class TTLCache(BaseCacheImpl[KT, VT]):
    def __init__(
        self,
        maxsize: int,
        ttl: float,
        iterable: Union[Iterable[Tuple[KT, VT]], Dict[KT, VT]] = ...,
        *,
        capacity: int = ...,
    ) -> None:
        ...

class LRUCache(BaseCacheImpl[KT, VT]):
    def __init__(
        self,
        maxsize: int,
        iterable: Union[Iterable[Tuple[KT, VT]], Dict[KT, VT]] = ...,
        *,
        capacity: int = ...,
    ) -> None:
        ...

class LFUCache(BaseCacheImpl[KT, VT]):
    def __init__(
        self,
        maxsize: int,
        iterable: Union[Iterable[Tuple[KT, VT]], Dict[KT, VT]] = ...,
        *,
        capacity: int = ...,
    ) -> None:
        ...

class VTTLCache(BaseCacheImpl[KT, VT]):
    def __init__(
        self,
        maxsize: int,
        iterable: Union[Iterable[Tuple[KT, VT]], Dict[KT, VT]] = ...,
        ttl: Optional[float] = 0.0,
        *,
        capacity: int = ...,
    ) -> None:
        ...

_CacheType = TypeVar("_CacheType", bound=BaseCacheImpl)

def cached(cache: typing.Optional[_CacheType], key_maker: typing.Optional[Callable[[tuple, dict], typing.Hashable]] = ..., clear_reuse: bool = ..., callback: typing.Optional[Callable[[int, typing.Any, typing.Any], typing.Any]] = ..., copy_level: int = ..., always_copy: typing.Optional[bool] = ...) -> Callable[[_F], _F]: ...
def cachedmethod(cache: typing.Optional[_CacheType], key_maker: typing.Optional[Callable[[tuple, dict], typing.Hashable]] = ..., clear_reuse: bool = ..., callback: typing.Optional[Callable[[int, typing.Any, typing.Any], typing.Any]] = ..., copy_level: int = ..., always_copy: typing.Optional[bool] = ...) -> Callable[[_F], _F]: ...
```

### klepto

For advanced caching workflows, `klepto` provides a highly flexible solution supporting both in-memory and persistent backends like file archives, SQL databases, and HDF5 files. It allows customizing how cache keys are generated and extends the standard cache eviction policies.

- **Backends**: In-memory dict, file archives, SQL databases, HDF5 files
- **Eviction Policies**: Same as `functools` plus LFU, MRU, RR
- **Key Mapping**: `hashmap`, `stringmap`, `picklemap` algorithms to generate keys
- **Persistence**: Archives cache to disk or database for long-term storage
- **Concurrency**: Locking for thread-safety, some process-safety depending on backend
- **Best For**: Complex scenarios needing transient and persistent caching

```pyi
### key maps
class keymap:
    def __init__(self, typed: bool = False, flat: bool = True,
                 sentinel: object=...) -> None: ...
    def __call__(self, *args, **kwargs) -> object: ...

class hashmap(keymap):
    def __init__(self, algorithm: Optional[str] = None,
                 typed: bool = False, flat: bool = True,
                 sentinel: object=...) -> None: ...

class stringmap(keymap):
    def __init__(self, encoding: Optional[str] = None,
                 typed: bool = False, flat: bool = True,
                 sentinel: object=...) -> None: ...

class picklemap(keymap):
    def __init__(self, serializer: Optional[str] = None,
                 typed: bool = False, flat: bool = True,
                 sentinel: object=...) -> None: ...

### base archive
class archive(dict):
    def __init__(self, *args, **kwds) -> None: ...
    def __asdict__(self) -> dict: ...
    def __repr__(self) -> str: ...
    def copy(self, name: Optional[str] = None) -> 'archive': ...
    def load(self, *args) -> None: ...
    def dump(self, *args) -> None: ...
    def archived(self, *on) -> bool: ...
    def sync(self, clear: bool = False) -> None: ...
    def drop(self) -> None: ...
    def open(self, archive: 'archive') -> None: ...

    @property
    def archive(self) -> 'archive': ...
    @archive.setter
    def archive(self, archive: 'archive') -> None: ...
    @property
    def name(self) -> str: ...
    @name.setter
    def name(self, archive: 'archive') -> None: ...
    @property
    def state(self) -> dict: ...
    @state.setter
    def state(self, archive: 'archive') -> None: ...

class dict_archive(archive):
    def __init__(self, *args, **kwds) -> None: ...

class null_archive(archive):
    def __init__(self, *args, **kwds) -> None: ...

class file_archive(archive):
    def __init__(self, filename: Optional[str] = None, dict: Optional[dict] = None,
                 cached: bool = True, serialized: bool = True,
                 protocol: Optional[int] = None, *args, **kwds) -> None: ...

class dir_archive(archive):
    def __init__(self, dirname: Optional[str] = None, dict: Optional[dict] = None,
                 cached: bool = True, serialized: bool = True,
                 compression: int = 0, permissions: Optional[int] = None,
                 memmode: Optional[str] = None, memsize: int = 100,
                 protocol: Optional[int] = None, *args, **kwds) -> None: ...

class sqltable_archive(archive):
    def __init__(self, database: Optional[str] = None,
                 table: Optional[str] = None, dict: Optional[dict] = None,
                 cached: bool = True, serialized: bool = True,
                 protocol: Optional[int] = None, *args, **kwds) -> None: ...

class sql_archive(archive):
    def __init__(self, database: Optional[str] = None, dict: Optional[dict] = None,
                 cached: bool = True, serialized: bool = True,
                 protocol: Optional[int] = None, *args, **kwds) -> None: ...

class hdfdir_archive(archive):
    def __init__(self, dirname: Optional[str] = None, dict: Optional[dict] = None,
                 cached: bool = True, serialized: bool = True,
                 permissions: Optional[int] = None,
                 protocol: Optional[int] = None, *args, **kwds) -> None: ...

class hdf_archive(archive):
    def __init__(self, filename: Optional[str] = None, dict: Optional[dict] = None,
                 cached: bool = True, serialized: bool = True,
                 protocol: Optional[int] = None, *args, **kwds) -> None: ...
```

### diskcache

When caching large datasets that should survive process restarts, `diskcache` shines with its optimized disk-backed storage using SQLite and the filesystem. It offers a range of eviction policies, a sharded `FanoutCache`, and persistent data structures like `Deque` and `Index`.

- **Backend**: SQLite for metadata, filesystem for data
- **Eviction Policies**: Configurable, including LRU and LFU
- **Persistence**: Data persists on disk between process runs
- **Concurrency**: Thread and process-safe 
- **Added Features**: Stampede prevention, throttling, optimized I/O
- **Best For**: Persistent caching for web apps and data pipelines

```pyi
### diskcache.pyi (Partial - Most important classes)

import typing
from typing import Callable, List, Dict, Any, IO, Optional, Tuple, Union

class Cache:
    def __init__(self, directory: Optional[str] = ..., timeout: float = ..., disk: Type[Disk] = ..., **settings: Any) -> None: ...
    @property
    def directory(self) -> str: ...
    @property
    def timeout(self) -> float: ...
    @property
    def disk(self) -> Disk: ...
    def set(self, key: Any, value: Any, expire: Optional[float] = ..., read: bool = ..., tag: Optional[str] = ..., retry: bool = ...) -> bool: ...
    def get(self, key: Any, default: Optional[Any] = ..., read: bool = ..., expire_time: bool = ..., tag: bool = ..., retry: bool = ...) -> Any: ...
    def delete(self, key: Any, retry: bool = ...) -> bool: ...
    def clear(self, retry: bool = ...) -> int: ...
    def volume(self) -> int: ...
    def check(self, fix: bool = ..., retry: bool = ...) -> List[warnings.WarningMessage]: ...
    def transact(self, retry: bool = ...) -> ContextManager[Callable]: ...
    def memoize(self, name: Optional[str] = ..., typed: bool = ..., expire: Optional[float] = ..., tag: Optional[str] = ..., ignore: typing.Iterable[str] = ...) -> Callable[[_F], _F]: ...
    def close(self) -> None: ...
    def volume(self) -> int: ...
    def stats(self, enable: bool = ..., reset: bool = ...) -> Tuple[int, int]: ...
    def volume(self) -> int: ...

class FanoutCache:
    def __init__(self, directory: Optional[str] = ..., shards: int = ..., timeout: float = ..., disk: Type[Disk] = ..., **settings: Any) -> None: ...
    @property
    def directory(self) -> str: ...
    def transact(self, retry: bool = ...) -> ContextManager[Callable]: ...
    def set(self, key: Any, value: Any, expire: Optional[float] = ..., read: bool = ..., tag: Optional[str] = ..., retry: bool = ...) -> bool: ...
    def get(self, key: Any, default: Optional[Any] = ..., read: bool = ..., expire_time: bool = ..., tag: bool = ..., retry: bool = ...) -> Any: ...
    def delete(self, key: Any, retry: bool = ...) -> bool: ...
    def clear(self, retry: bool = ...) -> int: ...
    def volume(self) -> int: ...
    def stats(self, enable: bool = ..., reset: bool = ...) -> Tuple[int, int]: ...
    def memoize(self, name: Optional[str] = ..., typed: bool = ..., expire: Optional[float] = ..., tag: Optional[str] = ..., ignore: typing.Iterable[str] = ...) -> Callable[[_F], _F]: ...
    def close(self) -> None: ...
    def volume(self) -> int: ...

class Disk:
    def __init__(self, directory: str, min_file_size: int = ..., pickle_protocol: int = ...) -> None: ...
    @property
    def min_file_size(self) -> int: ...
    @property
    def pickle_protocol(self) -> int: ...
    def put(self, key: Any) -> Tuple[Union[str, sqlite3.Binary, int, float], bool]: ...
    def get(self, key: Union[str, sqlite3.Binary, int, float], raw: bool) -> Any: ...
    def store(self, value: Any, read: bool, key: Constant = ...) -> Tuple[int, int, Optional[str], Optional[Union[str, sqlite3.Binary, int, float]]]: ...
    def fetch(self, mode: int, filename: Optional[str], value: Optional[Union[str, sqlite3.Binary, int, float]], read: bool) -> Any: ...

class JSONDisk(Disk):
    def __init__(self, directory: str, compress_level: int = ..., **kwargs: Any) -> None: ...
```

### joblib

Designed for scientific computing and ML workflows, `joblib` offers transparent disk-caching for functions, with optimizations for large NumPy arrays. Results are saved to disk and only re-computed when inputs change.

- **Backend**: Filesystem
- **Persistence**: Caches results to disk for costly computations
- **Memoization**: `@memory.cache` decorator for functions
- **Serialization**: Pickle-based with optional compression
- **Concurrency**: Process-safe file locking
- **Best For**: Caching ML models, features, large NumPy arrays

```pyi
### joblib.pyi (Partial - Most important classes and functions)

import typing
from typing import Callable, List, Dict, Any, IO, Optional, Tuple, Union

_F = TypeVar("_F", bound=Callable[..., Any])

class Memory:
    def __init__(self, location: Optional[str] = ..., backend: str = ..., verbose: int = ..., bytes_limit: Optional[Union[int, str]] = ..., mmap_mode: Optional[str] = ..., compress: Union[bool, int] = ..., backend_options: Optional[Dict[str, Any]] = ...) -> None: ...
    @property
    def location(self) -> str: ...
    @property
    def backend(self) -> str: ...
    @property
    def compress(self) -> Union[bool, int]: ...
    @property
    def verbose(self) -> int: ...
    def cache(self, func: Optional[_F] = ..., ignore: Optional[List[str]] = ..., verbose: Optional[int] = ..., mmap_mode: Optional[str] = ..., cache_validation_callback: Optional[Callable[[Dict[str, Any]], bool]] = ...) -> _F: ...
    def clear(self, warn: bool = ...) -> None: ...
    def eval(self, func: _F, *args: Any, **kwargs: Any) -> Any: ...
    def __call__(self, func: _F, *args: Any, **kwargs: Any) -> Any: ...

class Parallel:
    def __init__(self, n_jobs: Optional[int] = ..., backend: Optional[str] = ..., verbose: int = ..., timeout: Optional[float] = ..., pre_dispatch: Union[str, int] = ..., batch_size: Union[str, int] = ..., temp_folder: Optional[str] = ..., max_nbytes: Optional[Union[int, str]] = ..., mmap_mode: Optional[str] = ..., prefer: Optional[str] = ..., require: Optional[str] = ...) -> None: ...
    def __call__(self, iterable: typing.Iterable) -> List[Any]: ...
    def __enter__(self) -> "Parallel": ...
    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_value: Optional[BaseException], traceback: Optional[TracebackType]) -> None: ...
    def submit(self, func: _F, *args: Any, **kwargs: Any) -> concurrent.futures.Future: ...
    def map(self, func: _F, *iterables: typing.Iterable, timeout: Optional[float] = ..., chunksize: int = ...) -> typing.Iterable[Any]: ...
    def dispatch_next(self) -> None: ...
    def print_progress(self) -> None: ...
    def clear(self) -> None: ...
    def __len__(self) -> int: ...

def delayed(function: _F) -> Callable[..., Tuple[Callable, tuple, dict]]: ...
def cpu_count(only_physical_cores: bool = ...) -> int: ...
def effective_n_jobs(n_jobs: int = ...) -> int: ...
def hash(obj: Any, hash_name: str = ..., coerce_mmap: bool = ...) -> str: ...
def dump(value: Any, filename: Union[str, PathLikeStr], compress: Union[bool, int] = ..., protocol: Optional[int] = ..., cache_size: Optional[int] = ...) -> List[str]: ...
def load(filename: Union[str, PathLikeStr], mmap_mode: Optional[str] = ...) -> Any: ...
def register_parallel_backend(name: str, factory: Callable[..., ParallelBackendBase], make_default: bool = ...) -> None: ...

#### aiocache

Built for async applications using the `asyncio` framework, `aiocache` enables non-blocking caching operations. It provides both in-memory (`SimpleMemoryCache`) and distributed options (`RedisCache`, `MemcachedCache`).

- **Backends**: In-memory, Redis, Memcached
- **Async Decorators**: `@cached`, `@cached_stampede`, `@multi_cached`  
- **Serialization**: Pluggable, defaults to JSON
- **Best For**: Asynchronous web frameworks (FastAPI, Sanic), distributed caching

```pyi
### aiocache.pyi (Partial - Most important classes and decorators)

import typing
from typing import Any, Callable, Coroutine, Dict, List, Optional, Tuple, Type, Union

_F = typing.TypeVar("_F", bound=Callable[..., Any])

class BaseCache:
    NAME: str
    def __init__(self, serializer: Optional[BaseSerializer] = ..., plugins: Optional[List[BasePlugin]] = ..., namespace: Optional[str] = ..., timeout: float = ..., ttl: Optional[int] = ...) -> None: ...
    @classmethod
    def parse_uri_path(cls, path: str) -> Dict[str, str]: ...
    async def add(self, key: str, value: Any, ttl: Optional[int] = ..., dumps_fn: Optional[Callable[[Any], bytes]] = ..., namespace: Optional[str] = ..., timeout: Optional[int] = ...) -> bool: ...
    async def get(self, key: str, default: Optional[Any] = ..., loads_fn: Optional[Callable[[bytes], Any]] = ..., namespace: Optional[str] = ..., timeout: Optional[int] = ...) -> Any: ...
    async def multi_get(self, keys: List[str], loads_fn: Optional[Callable[[bytes], Any]] = ..., namespace: Optional[str] = ..., timeout: Optional[int] = ...) -> List[Any]: ...
    async def set(self, key: str, value: Any, ttl: Optional[int] = ..., dumps_fn: Optional[Callable[[Any], bytes]] = ..., namespace: Optional[str] = ..., timeout: Optional[int] = ..., _cas_token: Optional[Any] = ...) -> bool: ...
    async def multi_set(self, pairs: List[Tuple[str, Any]], ttl: Optional[int] = ..., dumps_fn: Optional[Callable[[Any], bytes]] = ..., namespace: Optional[str] = ..., timeout: Optional[int] = ...) -> bool: ...
    async def delete(self, key: str, namespace: Optional[str] = ..., timeout: Optional[int] = ...) -> int: ...
    async def exists(self, key: str, namespace: Optional[str] = ..., timeout: Optional[int] = ...) -> bool: ...
    async def increment(self, key: str, delta: int = ..., namespace: Optional[str] = ..., timeout: Optional[int] = ...) -> int: ...
    async def expire(self, key: str, ttl: Optional[int] = ..., namespace: Optional[str] = ..., timeout: Optional[int] = ...) -> bool: ...
    async def clear(self, namespace: Optional[str] = ..., timeout: Optional[int] = ...) -> bool: ...
    async def close(self, timeout: Optional[int] = ...) -> bool: ...
    async def raw(self, command: str, *args: Any, encoding: Optional[str] = ..., timeout: Optional[int] = ..., **kwargs: Any) -> Any: ...

class SimpleMemoryCache(BaseCache):
    NAME: str
    def __init__(self, serializer: Optional[BaseSerializer] = ..., **kwargs: Any) -> None: ...

class RedisCache(BaseCache):
    NAME: str
    def __init__(self, serializer: Optional[BaseSerializer] = ..., **kwargs: Any) -> None: ...

class MemcachedCache(BaseCache):
    NAME: str
    def __init__(self, serializer: Optional[BaseSerializer] = ..., **kwargs: Any) -> None: ...

class BaseSerializer:
    DEFAULT_ENCODING: Optional[str]
    def __init__(self, *args: Any, encoding: Union[str, object] = ..., **kwargs: Any) -> None: ...
    def dumps(self, value: Any) -> bytes: ...
    def loads(self, value: bytes) -> Any: ...

class JsonSerializer(BaseSerializer):
    def dumps(self, value: Any) -> str: ...
    def loads(self, value: str) -> Any: ...

class PickleSerializer(BaseSerializer):
    def dumps(self, value: Any) -> bytes: ...
    def loads(self, value: bytes) -> Any: ...

class NullSerializer(BaseSerializer):
    def dumps(self, value: Any) -> Any: ...
    def loads(self, value: Any) -> Any: ...

class BasePlugin:
    async def pre_get(self, client: BaseCache, key: str, namespace: Optional[str], **kwargs: Any) -> None: ...
    async def post_get(self, client: BaseCache, key: str, namespace: Optional[str], rv: Any, **kwargs: Any) -> None: ...
    # ... (and similar methods for other cache operations)

_Cache = TypeVar("_Cache", bound=BaseCache)

def cached(
    ttl: Optional[int] = ...,
    key: Optional[str] = ...,
    key_builder: Optional[Callable[..., str]] = ...,
    namespace: Optional[str] = ...,
    cache: Union[Type[_Cache], str] = ...,
    serializer: Optional[BaseSerializer] = ...,
    plugins: Optional[List[BasePlugin]] = ...,
    alias: Optional[str] = ...,
    noself: bool = ...,
    skip_cache_func: Optional[Callable[[Any], bool]] = ...,
    **kwargs: Any
) -> Callable[[_F], _F]: ...

def cached_stampede(
    lease: int = ...,
    ttl: Optional[int] = ...,
    key: Optional[str] = ...,
    key_builder: Optional[Callable[..., str]] = ...,
    namespace: Optional[str] = ...,
    cache: Union[Type[_Cache], str] = ...,
    serializer: Optional[BaseSerializer] = ...,
    plugins: Optional[List[BasePlugin]] = ...,
    alias: Optional[str] = ...,
    noself: bool = ...,
    skip_cache_func: Optional[Callable[[Any], bool]] = ...,
    **kwargs: Any
) -> Callable[[_F], _F]: ...

def multi_cached(
    keys_from_attr: Optional[str] = ...,
    namespace: Optional[str] = ...,
    key_builder: Optional[Callable[..., str]] = ...,
    ttl: Optional[int] = ...,
    cache: Union[Type[_Cache], str] = ...,
    serializer: Optional[BaseSerializer] = ...,
    plugins: Optional[List[BasePlugin]] = ...,
    alias: Optional[str] = ...,
    skip_cache_func: Optional[Callable[[str, Any], bool]] = ...,
    **kwargs: Any
) -> Callable[[_F], _F]: ...
```

### Summary of type hints

```pyi
### Type Stubs for Caching Libraries

from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Type,
    Iterable,
    Tuple,
    Union,
    TypeVar,
    Generic,
)
import datetime
import logging
from typing_extensions import Literal  # For older Python versions
```

*   **Generics:** For generic types like `Cache`, `FIFOCache`, `LFUCache`, etc. (in `cachetools`, `cachebox`, `klepto`) , I've used `TypeVar` to represent the key (`KT`) and value (`VT`) types.  This gives better type hinting.
*   **`object` as Default:** Where the original code uses implicit dynamic typing (no explicit type) or uses an internal implementation detail, I've often used `object` as the most general type hint.  This avoids creating stubs for internal classes.
*   **`NotImplementedError` and `typing.NoReturn`:** I've used `typing.NoReturn` for methods that are *not implemented* in a base class.  This is more precise than raising `NotImplementedError`, which would imply that a subclass *should* implement it.
*   **`defaultdict`:**  I've handled cases where `defaultdict` is used internally, providing a default factory function.
*   **`_Conn`:**  This internal helper class from `aiocache` is fully defined as all its methods are based on exported API.
* **`_DISTUTILS_PATCH`, `VIRTUALENV_PATCH_FILE`, etc.:** These internal constants/classes, used for patching `distutils`, are omitted.
*   **`kwargs` Handling:** In many cases, I've used `**kwargs` to represent arbitrary keyword arguments, especially when those arguments are passed directly to another function (like `open` or a backend-specific constructor).
* **`functools`:** The return type of decorators (`lru_cache`, `cache`) is `Callable[[Callable[..., R]], Callable[..., R]]`.  I've used a `TypeVar` named `_R` to make the relationship between the input and output types clear.
* **`klepto` classes**: Added the API for the `archive`, `dir_archive`, `sql_archive`, `sqltable_archive` based on the source code.
* **`joblib` classes**: Added the classes in the public API, `Memory`, `MemorizedFunc`, `NotMemorizedFunc`.

#### Recommendations

The best caching library depends on your specific needs - whether you require persistence, have large datasets, need multi-process safety, or are using an async framework. By understanding the strengths of each library, you can make an informed choice to optimize your application's performance.

---

_**Assistant**_

I'll update the TODO.md file to incorporate caching capabilities into the opero package, using twat-cache and twat-mp as dependencies. I'll organize the functionalities in a logical order.

---

_****_



---

_****_



---



---


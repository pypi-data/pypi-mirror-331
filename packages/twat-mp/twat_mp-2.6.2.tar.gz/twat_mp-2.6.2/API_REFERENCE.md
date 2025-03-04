# twat-mp API Reference

This document provides a comprehensive reference for the `twat-mp` package's API.

## Table of Contents

- [Core Classes](#core-classes)
  - [MultiPool](#multipool)
  - [ProcessPool](#processpool)
  - [ThreadPool](#threadpool)
  - [AsyncMultiPool](#asyncmultipool)
- [Decorators](#decorators)
  - [pmap](#pmap)
  - [imap](#imap)
  - [amap](#amap)
  - [apmap](#apmap)
- [Usage Patterns](#usage-patterns)
  - [Choosing the Right Pool](#choosing-the-right-pool)
  - [Error Handling](#error-handling)
  - [Resource Management](#resource-management)

## Core Classes

### MultiPool

```python
class MultiPool:
    def __init__(self, pool_class=PathosProcessPool, nodes=None):
        ...
```

Base class for managing Pathos parallel processing pools. This class abstracts the creation and cleanup of a parallel processing pool, automatically choosing the number of nodes (processes or threads) based on the CPU count if not provided.

**Parameters:**
- `pool_class`: The Pathos pool class to instantiate (default: `PathosProcessPool`)
- `nodes`: The number of processes/threads to use (default: CPU count)

**Methods:**
- `__enter__()`: Enter the runtime context and create the pool
- `__exit__(exc_type, exc_value, traceback)`: Exit the runtime context, ensuring the pool is properly closed and resources are freed

**Example:**
```python
with MultiPool(pool_class=PathosProcessPool) as pool:
    results = pool.map(lambda x: x * 2, range(5))
print(list(results))
```

### ProcessPool

```python
class ProcessPool(MultiPool):
    def __init__(self, nodes=None):
        ...
```

Context manager specifically for creating a process-based pool. This subclass of MultiPool defaults to using the ProcessPool from Pathos.

**Parameters:**
- `nodes`: Number of processes to use (default: CPU count)

**Example:**
```python
with ProcessPool() as pool:
    results = pool.map(lambda x: x * 2, range(10))
```

### ThreadPool

```python
class ThreadPool(MultiPool):
    def __init__(self, nodes=None):
        ...
```

Context manager specifically for creating a thread-based pool. This subclass of MultiPool defaults to using the ThreadPool from Pathos.

**Parameters:**
- `nodes`: Number of threads to use (default: CPU count)

**Example:**
```python
with ThreadPool() as pool:
    results = pool.map(lambda x: x * 2, range(10))
```

### AsyncMultiPool

```python
class AsyncMultiPool:
    def __init__(self, processes=None, initializer=None, initargs=None, **kwargs):
        ...
```

A context manager for managing an aiomultiprocess.Pool. Provides high-level interface for parallel processing with async/await support.

**Parameters:**
- `processes`: Number of processes to use (default: CPU count)
- `initializer`: Optional callable to initialize worker processes
- `initargs`: Arguments to pass to the initializer
- `**kwargs`: Additional keyword arguments passed to aiomultiprocess.Pool

**Methods:**
- `__aenter__()`: Enter the async context, creating and starting the pool
- `__aexit__(exc_type, exc_val, exc_tb)`: Exit the async context, closing and joining the pool
- `map(func, iterable)`: Apply the function to each item in the iterable in parallel
- `starmap(func, iterable)`: Like map() but unpacks arguments from the iterable
- `imap(func, iterable)`: Async iterator version of map()

**Example:**
```python
async def process_items():
    async with AsyncMultiPool() as pool:
        async def work(x):
            await asyncio.sleep(0.1)  # Some async work
            return x * 2

        results = await pool.map(work, range(10))
        return results
```

## Decorators

### pmap

```python
@pmap
def func(x):
    ...
```

Standard parallel map decorator (eager evaluation). Wraps a function so that when it is called with an iterable, the function is applied in parallel using a ProcessPool.

**Example:**
```python
@pmap
def square(x):
    return x * x

results = list(square(range(10)))
```

### imap

```python
@imap
def func(x):
    ...
```

Lazy parallel map decorator that returns an iterator. Results are yielded as they become available.

**Example:**
```python
@imap
def cube(x):
    return x * x * x

for result in cube(range(5)):
    print(result)  # Prints results as they become available
```

### amap

```python
@amap
def func(x):
    ...
```

Asynchronous parallel map decorator with automatic result retrieval. Uses the 'amap' method of Pathos pools.

**Example:**
```python
@amap
def double(x):
    return x * 2

results = list(double(range(10)))
```

### apmap

```python
@apmap
async def func(x):
    ...
```

Decorator for async functions to run in parallel using AsyncMultiPool. Requires the 'aio' extra to be installed.

**Example:**
```python
@apmap
async def double(x):
    await asyncio.sleep(0.1)  # Some async work
    return x * 2

async def main():
    results = await double(range(10))
    print(results)

asyncio.run(main())
```

## Usage Patterns

### Choosing the Right Pool

- **ProcessPool**: Best for CPU-intensive tasks that benefit from parallel execution across multiple cores
- **ThreadPool**: Best for I/O-bound tasks where threads can efficiently wait for I/O operations
- **AsyncMultiPool**: Best for combining async/await with multiprocessing, particularly useful for mixed workloads

### Error Handling

All pools provide proper error propagation. Exceptions raised in worker processes/threads are propagated to the main process:

```python
try:
    with ProcessPool() as pool:
        results = list(pool.map(potentially_failing_function, data))
except Exception as e:
    print(f"An error occurred: {e}")
```

### Resource Management

The context manager pattern ensures proper cleanup of resources:

```python
# Resources are automatically cleaned up when exiting the context
with ProcessPool() as pool:
    # Use the pool
    results = pool.map(func, data)

# Pool is now closed and resources are freed
```

For async pools:

```python
async def main():
    async with AsyncMultiPool() as pool:
        # Use the pool
        results = await pool.map(async_func, data)

    # Pool is now closed and resources are freed

asyncio.run(main())
```

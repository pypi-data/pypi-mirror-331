#!/usr/bin/env python3
# /// script
# dependencies = ["aiomultiprocess"]
# ///
# this_file: src/twat_mp/async_mp.py

"""
Asynchronous multiprocessing pool implementation using aiomultiprocess.
This module provides a high-level interface for parallel processing with async/await support.
"""

from functools import wraps
from typing import Any, AsyncIterator, Awaitable, Callable, Iterable, TypeVar, cast

HAS_AIOMULTIPROCESS = False
try:
    import aiomultiprocess

    HAS_AIOMULTIPROCESS = True
except ImportError:
    aiomultiprocess = None

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


def _check_aiomultiprocess() -> None:
    """
    Check if aiomultiprocess is available and raise a standardized ImportError if not.

    This is a utility function used throughout the module to ensure consistent
    error messages when the optional aiomultiprocess dependency is not installed.

    Raises:
        ImportError: If aiomultiprocess is not installed, with instructions on how to install it.
    """
    if not HAS_AIOMULTIPROCESS:
        raise ImportError(
            "Required dependency 'aiomultiprocess' is not installed. "
            "Please install it with: pip install 'twat-mp[aio]' or pip install aiomultiprocess"
        )


class AsyncMultiPool:
    """
    A context manager for managing an aiomultiprocess.Pool.
    Provides high-level interface for parallel processing with async/await support.

    This class combines the benefits of async/await with multiprocessing, allowing
    for efficient parallel execution of CPU-bound tasks within an asynchronous context.
    It automatically manages the lifecycle of the underlying aiomultiprocess.Pool.

    Attributes:
        processes: Number of worker processes to use. If None, uses CPU count.
        initializer: Optional callable to initialize worker processes.
        initargs: Arguments to pass to the initializer.
        pool: The underlying aiomultiprocess.Pool instance.

    Example:
        ```python
        import asyncio

        async def process_data():
            # Create a pool with 4 worker processes
            async with AsyncMultiPool(processes=4) as pool:
                # Define an async worker function
                async def work(item):
                    await asyncio.sleep(0.1)  # Simulate I/O
                    return item * 2

                # Process items in parallel
                results = await pool.map(work, range(10))
                print(results)  # [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

                # Using starmap for unpacking arguments
                async def add(a, b):
                    await asyncio.sleep(0.1)
                    return a + b

                sum_results = await pool.starmap(add, [(1, 2), (3, 4), (5, 6)])
                print(sum_results)  # [3, 7, 11]

                # Using imap for processing results as they arrive
                async for result in pool.imap(work, range(5)):
                    print(f"Got result: {result}")

        asyncio.run(process_data())
        ```
    """

    def __init__(
        self,
        processes: int | None = None,
        initializer: Callable[..., Any] | None = None,
        initargs: tuple[Any, ...] | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize an AsyncMultiPool.

        Args:
            processes: Number of processes to use. If None, uses CPU count.
            initializer: Optional callable to initialize worker processes.
            initargs: Arguments to pass to the initializer.
            **kwargs: Additional keyword arguments passed to aiomultiprocess.Pool.

        Raises:
            ImportError: If aiomultiprocess is not installed.
        """
        _check_aiomultiprocess()
        self.processes = processes
        self.initializer = initializer
        self.initargs = initargs or ()
        self.kwargs = kwargs
        self.pool: aiomultiprocess.Pool | None = None

    async def __aenter__(self) -> "AsyncMultiPool":
        """Enter the async context, creating and starting the pool."""
        _check_aiomultiprocess()
        self.pool = aiomultiprocess.Pool(
            self.processes,
            initializer=self.initializer,
            initargs=self.initargs,
            **self.kwargs,
        )
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Exit the async context, closing and joining the pool.

        This method ensures proper cleanup of resources even if an exception occurs.
        It attempts to gracefully close the pool first, then joins it to wait for
        all running tasks to complete.

        Args:
            exc_type: The exception type if an exception was raised.
            exc_val: The exception value if an exception was raised.
            exc_tb: The traceback if an exception was raised.
        """
        if self.pool:
            try:
                # Use close() for graceful shutdown instead of terminate()
                # This allows running tasks to complete
                self.pool.close()
                await self.pool.join()
            except Exception as e:
                # If close/join fails, fall back to terminate()
                try:
                    self.pool.terminate()
                    await self.pool.join()
                except Exception:
                    # Last resort: just set pool to None and let GC handle it
                    pass
                # Log error or handle it appropriately
                if exc_type is None:
                    # If no previous exception, raise the cleanup exception
                    raise RuntimeError(f"Error during pool cleanup: {e}") from e
            finally:
                self.pool = None

    async def map(
        self, func: Callable[[T], Awaitable[U]], iterable: Iterable[T]
    ) -> list[U]:
        """
        Apply the function to each item in the iterable in parallel.

        This method distributes the workload across multiple processes and
        collects all results, returning them as a list in the same order
        as the input iterable.

        Args:
            func: Async function to apply to each item.
            iterable: Items to process.

        Returns:
            List of results in the order of input items.

        Raises:
            RuntimeError: If pool is not initialized.
            ImportError: If aiomultiprocess is not installed.

        Example:
            ```python
            async def double(x):
                await asyncio.sleep(0.1)  # Simulate I/O or CPU work
                return x * 2

            async with AsyncMultiPool() as pool:
                results = await pool.map(double, range(5))
                print(results)  # [0, 2, 4, 6, 8]
            ```
        """
        _check_aiomultiprocess()
        if not self.pool:
            raise RuntimeError("Pool not initialized. Use 'async with' statement.")
        return await self.pool.map(func, iterable)

    async def starmap(
        self,
        func: Callable[..., Awaitable[U]],
        iterable: Iterable[tuple[Any, ...]],
    ) -> list[U]:
        """
        Like map() but the elements of the iterable are expected to be iterables
        that are unpacked as arguments.

        This method is useful when you need to pass multiple arguments to the
        worker function. Each item in the iterable should be a tuple containing
        the arguments to pass to the function.

        Args:
            func: Async function to apply to each item.
            iterable: Items to process, each item being a tuple of arguments.

        Returns:
            List of results in the order of input items.

        Raises:
            RuntimeError: If pool is not initialized.
            ImportError: If aiomultiprocess is not installed.

        Example:
            ```python
            async def multiply(a, b):
                await asyncio.sleep(0.1)  # Simulate work
                return a * b

            async with AsyncMultiPool() as pool:
                # Process pairs of numbers
                results = await pool.starmap(
                    multiply,
                    [(1, 2), (3, 4), (5, 6)]
                )
                print(results)  # [2, 12, 30]
            ```
        """
        _check_aiomultiprocess()
        if not self.pool:
            raise RuntimeError("Pool not initialized. Use 'async with' statement.")
        return await self.pool.starmap(func, iterable)

    async def imap(
        self, func: Callable[[T], Awaitable[U]], iterable: Iterable[T]
    ) -> AsyncIterator[U]:
        """
        Async iterator version of map().

        This method returns an async iterator that yields results as they become
        available, which can be more efficient when processing large datasets or
        when you want to start processing results before all items are complete.

        Args:
            func: Async function to apply to each item.
            iterable: Items to process.

        Returns:
            Async iterator yielding results as they become available.

        Raises:
            RuntimeError: If pool is not initialized.
            ImportError: If aiomultiprocess is not installed.

        Example:
            ```python
            async def process_item(x):
                await asyncio.sleep(random.random())  # Variable processing time
                return x * 2

            async with AsyncMultiPool() as pool:
                # Process items and handle results as they arrive
                async for result in pool.imap(process_item, range(10)):
                    print(f"Received result: {result}")
                    # Results may arrive in any order due to variable processing time
            ```
        """
        _check_aiomultiprocess()
        if not self.pool:
            raise RuntimeError("Pool not initialized. Use 'async with' statement.")
        return cast(AsyncIterator[U], self.pool.imap(func, iterable))


def apmap(
    func: Callable[[T], Awaitable[U]],
) -> Callable[[Iterable[T]], Awaitable[list[U]]]:
    """
    Decorator that wraps a function to run it in parallel using AsyncMultiPool.

    This decorator simplifies the common pattern of creating a pool and mapping
    a function over an iterable. When the decorated function is called with an
    iterable, it automatically creates an AsyncMultiPool, maps the function over
    the iterable, and returns the results.

    Args:
        func: Async function to parallelize.

    Returns:
        Wrapped function that runs in parallel.

    Raises:
        ImportError: If aiomultiprocess is not installed.

    Example:
        ```python
        import asyncio

        # Decorate an async function for parallel execution
        @apmap
        async def double(x):
            await asyncio.sleep(0.1)  # Simulate work
            return x * 2

        async def main():
            # Call the decorated function with an iterable
            results = await double(range(10))
            print(results)  # [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

        asyncio.run(main())
        ```
    """
    _check_aiomultiprocess()

    @wraps(func)
    async def wrapper(iterable: Iterable[T]) -> list[U]:
        async with AsyncMultiPool() as pool:
            return await pool.map(func, iterable)

    return wrapper

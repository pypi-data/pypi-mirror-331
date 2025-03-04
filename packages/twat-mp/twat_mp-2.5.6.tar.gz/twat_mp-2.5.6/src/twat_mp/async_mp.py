#!/usr/bin/env python3
# /// script
# dependencies = ["aiomultiprocess"]
# ///
# this_file: src/twat_mp/async_mp.py

"""
Asynchronous multiprocessing pool implementation using aiomultiprocess.

This module provides a high-level interface for parallel processing with async/await support.
It allows for efficient execution of CPU-bound tasks within an asynchronous context by
leveraging multiple processes, each capable of running coroutines independently.

The main components are:
- AsyncMultiPool: A context manager for managing aiomultiprocess.Pool instances
- apmap: A decorator for easily applying async functions to iterables in parallel

Example:
    ```python
    import asyncio
    from twat_mp import AsyncMultiPool, apmap

    # Using the context manager directly
    async def main():
        async with AsyncMultiPool() as pool:
            async def work(x):
                await asyncio.sleep(0.1)  # Simulate I/O or CPU work
                return x * 2

            results = await pool.map(work, range(10))
            print(results)  # [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

    # Using the decorator
    @apmap
    async def process_item(x):
        await asyncio.sleep(0.1)
        return x * 3

    async def main2():
        results = await process_item(range(5))
        print(results)  # [0, 3, 6, 9, 12]

    asyncio.run(main())
    asyncio.run(main2())
    ```
"""

import logging
import traceback
from functools import wraps
from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Iterable,
    TypeVar,
    Optional,
)

# Set up logging
logger = logging.getLogger(__name__)

# Import aiomultiprocess conditionally to handle the case when it's not installed
HAS_AIOMULTIPROCESS = False
try:
    import aiomultiprocess
    from aiomultiprocess import Pool as AioPool

    HAS_AIOMULTIPROCESS = True
except ImportError:
    aiomultiprocess = None

    # Define a placeholder type for type checking
    class AioPool:  # type: ignore
        """Placeholder for aiomultiprocess.Pool when not available."""

        pass


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
        processes: Optional[int] = None,
        initializer: Optional[Callable[..., Any]] = None,
        initargs: Optional[tuple[Any, ...]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize an AsyncMultiPool.

        Args:
            processes: Number of processes to use. If None, uses CPU count.
                       For CPU-bound tasks, setting this to the number of CPU cores
                       typically provides optimal performance.
            initializer: Optional callable to initialize worker processes.
                         This is called once for each worker process when it starts.
            initargs: Arguments to pass to the initializer.
                      Only used if initializer is specified.
            **kwargs: Additional keyword arguments passed to aiomultiprocess.Pool.
                      See aiomultiprocess documentation for available options.

        Raises:
            ImportError: If aiomultiprocess is not installed.
        """
        _check_aiomultiprocess()
        self.processes = processes
        self.initializer = initializer
        self.initargs = initargs or ()
        self.kwargs = kwargs
        self.pool: Optional[AioPool] = None
        self._cleanup_attempted = False

    async def __aenter__(self) -> "AsyncMultiPool":
        """
        Enter the async context, creating and starting the pool.

        This method initializes the underlying aiomultiprocess.Pool with the
        parameters provided during initialization.

        Returns:
            The AsyncMultiPool instance (self) for method chaining.

        Raises:
            ImportError: If aiomultiprocess is not installed.
            RuntimeError: If pool creation fails.
        """
        _check_aiomultiprocess()
        if aiomultiprocess is not None:  # This check is for type checking only
            try:
                self.pool = aiomultiprocess.Pool(
                    self.processes,
                    initializer=self.initializer,
                    initargs=self.initargs,
                    **self.kwargs,
                )
                logger.debug(f"Created AsyncMultiPool with {self.processes} processes")
            except Exception as e:
                logger.error(f"Failed to create AsyncMultiPool: {e}")
                raise RuntimeError(f"Failed to create AsyncMultiPool: {e}") from e
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Exit the async context, closing and joining the pool.

        This method ensures proper cleanup of resources even if an exception occurs.
        It implements a robust cleanup strategy with multiple fallback mechanisms:

        1. First attempts a graceful shutdown with close() and join()
        2. If that fails, falls back to terminate() and join()
        3. If all cleanup attempts fail, ensures the pool reference is cleared

        The method also propagates any exceptions that occurred during cleanup
        if there wasn't already an exception in progress.

        Args:
            exc_type: The exception type if an exception was raised.
            exc_val: The exception value if an exception was raised.
            exc_tb: The traceback if an exception was raised.

        Raises:
            RuntimeError: If an error occurs during pool cleanup and no previous
                         exception was being handled.
        """
        if not self.pool:
            logger.debug("No pool to clean up in __aexit__")
            return

        # Avoid duplicate cleanup attempts
        if self._cleanup_attempted:
            logger.warning("Cleanup already attempted, skipping")
            return

        self._cleanup_attempted = True
        cleanup_error = None

        # Log if we're cleaning up due to an exception
        if exc_type:
            logger.warning(
                f"Cleaning up pool after exception: {exc_type.__name__}: {exc_val}"
            )

        try:
            # Step 1: Try graceful shutdown first
            logger.debug("Attempting graceful pool shutdown with close()")
            self.pool.close()
            await self.pool.join()
            logger.debug("Pool gracefully closed and joined")
        except Exception as e:
            # Log the error but continue with cleanup
            cleanup_error = e
            logger.error(f"Error during graceful pool shutdown: {e}")
            logger.debug(f"Traceback: {traceback.format_exc()}")

            try:
                # Step 2: Fall back to terminate if close fails
                logger.debug("Attempting forceful pool termination")
                self.pool.terminate()
                await self.pool.join()
                logger.debug("Pool forcefully terminated and joined")
            except Exception as e2:
                # Update the cleanup error but continue
                cleanup_error = e2
                logger.error(f"Error during forceful pool termination: {e2}")
                logger.debug(f"Traceback: {traceback.format_exc()}")
        finally:
            # Step 3: Always clear the pool reference
            logger.debug("Clearing pool reference")
            self.pool = None

        # If we had a cleanup error and no prior exception, raise the cleanup error
        if cleanup_error and not exc_type:
            error_msg = f"Error during pool cleanup: {cleanup_error}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from cleanup_error

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

        try:
            return await self.pool.map(func, iterable)
        except Exception as e:
            logger.error(f"Error during parallel map operation: {e}")
            raise RuntimeError(f"Error during parallel map operation: {e}") from e

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

        try:
            return await self.pool.starmap(func, iterable)
        except Exception as e:
            logger.error(f"Error during parallel starmap operation: {e}")
            raise RuntimeError(f"Error during parallel starmap operation: {e}") from e

    async def imap(
        self, func: Callable[[T], Awaitable[U]], iterable: Iterable[T]
    ) -> AsyncIterator[U]:
        """
        Async iterator version of map().

        This method returns an async iterator that yields results as they become
        available, which can be more memory-efficient for large datasets or when
        processing times vary significantly between items.

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
            async def process(x):
                await asyncio.sleep(random.random())  # Variable processing time
                return x * 2

            async with AsyncMultiPool() as pool:
                # Process and handle results as they arrive
                async for result in pool.imap(process, range(10)):
                    print(f"Got result: {result}")
            ```
        """
        _check_aiomultiprocess()
        if not self.pool:
            raise RuntimeError("Pool not initialized. Use 'async with' statement.")

        try:
            # Use explicit async for loop to yield results
            async for result in self.pool.imap(func, iterable):
                yield result
        except Exception as e:
            logger.error(f"Error during parallel imap operation: {e}")
            raise RuntimeError(f"Error during parallel imap operation: {e}") from e


def apmap(
    func: Callable[[T], Awaitable[U]],
) -> Callable[[Iterable[T]], Awaitable[list[U]]]:
    """
    Decorator for parallel processing of async functions.

    This decorator transforms an async function into one that can be applied
    to each item in an iterable in parallel using an AsyncMultiPool. It handles
    the creation and cleanup of the pool automatically.

    Args:
        func: The async function to parallelize.

    Returns:
        A wrapped async function that, when called with an iterable, applies
        the original function to each item in parallel and returns the results.

    Raises:
        ImportError: If aiomultiprocess is not installed.

    Example:
        ```python
        @apmap
        async def process(x):
            await asyncio.sleep(0.1)  # Simulate work
            return x * 3

        async def main():
            # This will process all items in parallel
            results = await process(range(5))
            print(results)  # [0, 3, 6, 9, 12]

        asyncio.run(main())
        ```
    """
    _check_aiomultiprocess()

    @wraps(func)
    async def wrapper(iterable: Iterable[T]) -> list[U]:
        """
        Apply the decorated async function to each item in the iterable in parallel.

        This wrapper function creates an AsyncMultiPool, uses it to apply the
        decorated function to each item in the iterable, and then cleans up the pool.

        Args:
            iterable: The items to process.

        Returns:
            A list of results from applying the function to each item.

        Raises:
            ImportError: If aiomultiprocess is not installed.
            RuntimeError: If pool creation or execution fails.
        """
        try:
            async with AsyncMultiPool() as pool:
                return await pool.map(func, iterable)
        except Exception as e:
            logger.error(f"Error in apmap decorator: {e}")
            raise RuntimeError(f"Error in parallel processing: {e}") from e

    return wrapper

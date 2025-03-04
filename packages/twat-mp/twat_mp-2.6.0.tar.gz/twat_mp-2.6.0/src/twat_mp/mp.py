"""
Parallel processing utilities using the Pathos multiprocessing library.

This module provides convenient context managers for creating and managing
parallel processing pools (process or thread based) and decorators for applying
parallel map operations to functions. It uses Pathos pools under the hood,
automatically determining the optimal number of processes/threads based on the
system's CPU count if not specified.

Example usage:
    >>> from mp import pmap, imap, amap, ProcessPool, ThreadPool
    >>>
    >>> # Using the parallel map decorator (synchronous mapping)
    >>> @pmap
    ... def square(x: int) -> int:
    ...     return x * x
    >>>
    >>> results = list(square(range(10)))
    >>> print(results)
    [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
"""

from __future__ import annotations

import logging
import os
import sys
import traceback
from functools import wraps
from typing import TYPE_CHECKING, Any, Literal, TypeVar

from pathos.helpers import mp  # Provides CPU count helper
from pathos.pools import ProcessPool as PathosProcessPool
from pathos.pools import ThreadPool as PathosThreadPool

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

# Set up logging
logger = logging.getLogger(__name__)

# Type variables for generality in mapping functions
T = TypeVar("T")
U = TypeVar("U")

# Define a union type for either a process pool or a thread pool from Pathos
PathosPool = PathosProcessPool | PathosThreadPool
"""Type alias for either a ProcessPool or ThreadPool from Pathos."""

# Debug mode flag - can be set via environment variable
DEBUG_MODE = os.environ.get("TWAT_MP_DEBUG", "0").lower() in ("1", "true", "yes", "on")


class WorkerError(Exception):
    """
    Exception raised when a worker process encounters an error.

    This exception wraps the original exception from the worker process and
    provides additional context about where and how the error occurred.

    Attributes:
        original_exception: The original exception raised in the worker process.
        worker_id: The ID of the worker process where the error occurred, if available.
        input_item: The input item that was being processed when the error occurred.
        traceback_str: The traceback string from the worker process, if available.
    """

    def __init__(
        self,
        message: str,
        original_exception: Exception | None = None,
        worker_id: int | None = None,
        input_item: Any = None,
        traceback_str: str | None = None,
    ) -> None:
        """
        Initialize a WorkerError.

        Args:
            message: A descriptive error message.
            original_exception: The original exception raised in the worker process.
            worker_id: The ID of the worker process where the error occurred.
            input_item: The input item that was being processed when the error occurred.
            traceback_str: The traceback string from the worker process.
        """
        self.original_exception = original_exception
        self.worker_id = worker_id
        self.input_item = input_item
        self.traceback_str = traceback_str

        # Build a detailed error message
        detailed_message = message
        if worker_id is not None:
            detailed_message += f" in worker {worker_id}"
        if input_item is not None:
            detailed_message += f" while processing {input_item!r}"
        if original_exception is not None:
            detailed_message += (
                f": {type(original_exception).__name__}: {original_exception}"
            )

        super().__init__(detailed_message)


def set_debug_mode(enabled: bool = True) -> None:
    """
    Enable or disable debug mode for detailed logging.

    When debug mode is enabled, the module will log detailed information about
    pool creation, task execution, and resource cleanup. This is useful for
    troubleshooting issues with parallel processing.

    Args:
        enabled: Whether to enable debug mode. Defaults to True.
    """
    global DEBUG_MODE
    DEBUG_MODE = enabled

    if enabled:
        # Configure logging for debug mode
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)],
        )
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled for twat_mp")
    else:
        # Reset to default logging level
        logger.setLevel(logging.INFO)
        logger.info("Debug mode disabled for twat_mp")


def _worker_wrapper(func: Callable[[T], U], item: T, worker_id: int | None = None) -> U:
    """
    Wrap a worker function to provide better error handling and context.

    This wrapper captures exceptions raised in worker functions and enriches them
    with additional context information before re-raising them.

    Args:
        func: The worker function to execute.
        item: The input item to process.
        worker_id: An optional identifier for the worker process.

    Returns:
        The result of applying the function to the item.

    Raises:
        WorkerError: If the worker function raises an exception, it's wrapped
                        in a WorkerError with additional context.
    """
    try:
        return func(item)
    except Exception as e:
        # Capture the traceback
        tb_str = traceback.format_exc()
        logger.error(
            f"Error in worker {worker_id if worker_id is not None else 'unknown'}: {e}"
        )
        logger.debug(f"Traceback: {tb_str}")

        # Wrap the exception with additional context
        raise WorkerError(
            "Worker process error",
            original_exception=e,
            worker_id=worker_id,
            input_item=item,
            traceback_str=tb_str,
        ) from e


class MultiPool:
    """
    Context manager for managing Pathos parallel processing pools.

    This class abstracts the creation and cleanup of a parallel processing pool.
    It automatically chooses the number of nodes (processes or threads) based on
    the CPU count if not provided. It can be subclassed for specific pool types.

    Attributes:
        pool_class: The Pathos pool class to instantiate.
        nodes: The number of processes/threads to use.
        pool: The actual pool instance (created on entering the context).

    Example:
        >>> with MultiPool(pool_class=PathosProcessPool) as pool:
        ...     results = pool.map(lambda x: x * 2, range(5))
        >>> print(list(results))
    """

    def __init__(
        self,
        pool_class: type[PathosPool] = PathosProcessPool,
        nodes: int | None = None,
        debug: bool | None = None,
    ) -> None:
        """
        Initialize the MultiPool context manager.

        Args:
            pool_class: The pool class to use (ProcessPool or ThreadPool).
                       Defaults to ProcessPool.
            nodes: The number of processes/threads to create.
                  If None, uses the CPU count.
            debug: Whether to enable debug mode for this pool instance.
                  If None, uses the global DEBUG_MODE setting.
        """
        self.pool_class = pool_class
        # If nodes is not specified, determine optimal number based on CPU count.
        self.nodes: int = nodes if nodes is not None else mp.cpu_count()  # type: ignore
        self.pool: PathosPool | None = None  # Pool will be created in __enter__
        self.debug = DEBUG_MODE if debug is None else debug

        if self.debug:
            logger.debug(
                f"Initializing {self.__class__.__name__} with {self.pool_class.__name__}, "
                f"nodes={self.nodes}"
            )

    def __enter__(self) -> PathosPool:
        """
        Enter the runtime context and create the pool.

        Returns:
            The instantiated pool object.

        Raises:
            RuntimeError: If pool creation fails.
        """
        if self.debug:
            logger.debug(f"Creating pool with {self.nodes} nodes")

        try:
            self.pool = self.pool_class(nodes=self.nodes)

            if self.debug:
                logger.debug(f"Pool created successfully: {self.pool}")

            if self.pool is None:
                # This should rarely happen; raise an error if pool instantiation fails.
                msg = f"Failed to create a pool using {self.pool_class}"
                logger.error(msg)
                raise RuntimeError(msg)

            # Patch the map method to use our wrapper for better error handling
            original_map = self.pool.map

            def enhanced_map(func: Callable[[T], U], iterable: Iterator[T]) -> Any:
                """Enhanced map function with better error propagation."""

                # Create a wrapper function that captures worker context
                def wrapped_func(item, idx=None):
                    return _worker_wrapper(func, item, idx)

                try:
                    return original_map(wrapped_func, iterable)
                except Exception as e:
                    # If it's already a WorkerError, just re-raise it
                    if isinstance(e, WorkerError):
                        raise

                    # Otherwise, wrap it with additional context
                    logger.error(f"Error during parallel map operation: {e}")
                    if self.debug:
                        logger.debug(f"Traceback: {traceback.format_exc()}")

                    raise RuntimeError(
                        f"Error during parallel map operation: {e}"
                    ) from e

            # Replace the map method with our enhanced version
            self.pool.map = enhanced_map  # type: ignore

            return self.pool

        except Exception as e:
            error_msg = f"Error creating pool: {e}"
            logger.error(error_msg)
            if self.debug:
                logger.debug(f"Traceback: {traceback.format_exc()}")
            raise RuntimeError(error_msg) from e

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> Literal[False]:
        """
        Exit the runtime context, ensuring the pool is properly closed and resources are freed.

        This method handles different cleanup scenarios based on the exception type:
        - For KeyboardInterrupt, it immediately terminates the pool for faster response
        - For normal exits, it gracefully closes the pool and waits for tasks to complete
        - For any cleanup failures, it attempts to terminate the pool as a fallback

        Args:
            exc_type: The exception type if an exception was raised.
            exc_value: The exception value if an exception was raised.
            traceback: The traceback if an exception was raised.

        Returns:
            False to indicate that any exception should be propagated.
        """
        if self.pool:
            # Log the exception if one occurred
            if exc_type is not None and self.debug:
                logger.debug(
                    f"Cleaning up pool after exception: {exc_type.__name__}: {exc_value}"
                )

            try:
                # Special handling for KeyboardInterrupt
                if exc_type is KeyboardInterrupt:
                    # Terminate immediately on keyboard interrupt for faster response
                    if self.debug:
                        logger.debug(
                            "KeyboardInterrupt detected, terminating pool immediately"
                        )
                    self.pool.terminate()
                    self.pool.join()
                    if self.debug:
                        logger.debug(
                            "Pool terminated and joined after KeyboardInterrupt"
                        )
                else:
                    # Normal graceful shutdown
                    # Close the pool and join to wait for all tasks to complete
                    if self.debug:
                        logger.debug("Closing pool gracefully")
                    self.pool.close()
                    self.pool.join()
                    if self.debug:
                        logger.debug("Pool closed and joined successfully")
            except Exception as e:
                # If close/join fails, ensure terminate is called
                if self.debug:
                    logger.debug(
                        f"Error during pool cleanup: {e}, attempting terminate"
                    )
                try:
                    self.pool.terminate()
                    self.pool.join()
                    if self.debug:
                        logger.debug("Pool terminated and joined after cleanup error")
                except Exception as e2:
                    # Last resort, just let it go
                    if self.debug:
                        logger.debug(f"Failed to terminate pool: {e2}")
                    pass
            finally:
                # Clear the pool to free up resources
                try:
                    if self.debug:
                        logger.debug("Clearing pool resources")
                    self.pool.clear()
                    if self.debug:
                        logger.debug("Pool resources cleared")
                except Exception as e:
                    if self.debug:
                        logger.debug(f"Error clearing pool resources: {e}")
                    pass
                self.pool = None
                if self.debug:
                    logger.debug("Pool reference set to None")
        elif self.debug:
            logger.debug("No pool to clean up")

        return False  # Propagate any exception that occurred


class ProcessPool(MultiPool):
    """
    Context manager specifically for creating a process-based pool.

    This subclass of MultiPool defaults to using the ProcessPool from Pathos.
    Process pools are ideal for CPU-bound tasks as they bypass the Global Interpreter Lock (GIL)
    and can utilize multiple CPU cores effectively.

    Example:
        >>> with ProcessPool() as pool:
        ...     results = pool.map(lambda x: x * 2, range(10))
    """

    def __init__(self, nodes: int | None = None, debug: bool | None = None) -> None:
        """
        Initialize a ProcessPool with an optional node count.

        Args:
            nodes: Number of processes to use. If None, defaults to the CPU count.
                   For CPU-bound tasks, setting this to the number of CPU cores
                   typically provides optimal performance.
            debug: Whether to enable debug mode for this pool instance.
                  If None, uses the global DEBUG_MODE setting.
        """
        super().__init__(pool_class=PathosProcessPool, nodes=nodes, debug=debug)


class ThreadPool(MultiPool):
    """
    Context manager specifically for creating a thread-based pool.

    This subclass of MultiPool defaults to using the ThreadPool from Pathos.
    Thread pools are ideal for I/O-bound tasks where processes would introduce
    unnecessary overhead. All threads share the same memory space, making them
    more efficient for tasks that don't require bypassing the GIL.

    Example:
        >>> with ThreadPool() as pool:
        ...     results = pool.map(lambda x: x * 2, range(10))
    """

    def __init__(self, nodes: int | None = None, debug: bool | None = None) -> None:
        """
        Initialize a ThreadPool with an optional node count.

        Args:
            nodes: Number of threads to use. If None, defaults to the CPU count.
                   For I/O-bound tasks, you may want to use more threads than CPU cores
                   to maximize throughput during I/O wait times.
            debug: Whether to enable debug mode for this pool instance.
                  If None, uses the global DEBUG_MODE setting.
        """
        super().__init__(pool_class=PathosThreadPool, nodes=nodes, debug=debug)


def mmap(
    how: str, *, get_result: bool = False, debug: bool | None = None
) -> Callable[[Callable[[T], U]], Callable[[Iterator[T]], Iterator[U]]]:
    """
    Create a decorator to perform parallel mapping using a specified Pathos pool method.

    The decorator wraps a function so that when it is called with an iterable,
    the function is applied in parallel using the specified mapping method.
    For asynchronous mapping (e.g., 'amap'), the result's `.get()` method can be
    automatically called to retrieve the computed values.

    Args:
        how: Name of the pool mapping method ('map', 'imap', or 'amap').
             - 'map': Standard parallel mapping, returns results in order
             - 'imap': Iterative mapping, returns results as they complete
             - 'amap': Asynchronous mapping, returns a future-like object
        get_result: If True, automatically call .get() on the result (useful for amap).
                    Defaults to False.
        debug: Whether to enable debug mode for operations using this decorator.
              If None, uses the global DEBUG_MODE setting.

    Returns:
        A decorator function that transforms the target function for parallel execution.

    Raises:
        ValueError: If the specified mapping method is not supported.
        RuntimeError: If pool creation fails.
        KeyboardInterrupt: If the user interrupts the execution.

    Example:
        >>> @mmap('map')
        ... def cube(x: int) -> int:
        ...     return x ** 3
        >>> results = list(cube(range(5)))
        >>> print(results)
        [0, 1, 8, 27, 64]
    """
    # Validate the mapping method early
    valid_methods = ["map", "imap", "amap"]
    if how not in valid_methods:
        raise ValueError(
            f"Invalid mapping method: '{how}'. Must be one of {valid_methods}"
        )

    # Use the global debug setting if not specified
    use_debug = DEBUG_MODE if debug is None else debug

    if use_debug:
        logger.debug(
            f"Creating mmap decorator with method={how}, get_result={get_result}"
        )

    def decorator(func: Callable[[T], U]) -> Callable[[Iterator[T]], Iterator[U]]:
        @wraps(func)
        def wrapper(iterable: Iterator[T], *args: Any, **kwargs: Any) -> Any:
            # Create a MultiPool context to manage the pool lifecycle
            if use_debug:
                logger.debug(
                    f"Executing {func.__name__} with {how} on {type(iterable).__name__}"
                )

            try:
                with MultiPool(debug=use_debug) as pool:
                    # Dynamically fetch the mapping method (map, imap, or amap)
                    try:
                        mapping_method = getattr(pool, how)
                        if use_debug:
                            logger.debug(f"Using pool method: {how}")
                    except AttributeError as err:
                        error_msg = f"Pool does not support mapping method: '{how}'"
                        logger.error(error_msg)
                        raise ValueError(error_msg) from err

                    try:
                        if use_debug:
                            logger.debug(f"Starting parallel execution with {how}")
                        result = mapping_method(func, iterable)
                        # For asynchronous mapping, call .get() to obtain the actual results
                        if get_result:
                            if use_debug:
                                logger.debug("Getting results from async operation")
                            result = result.get()
                        if use_debug:
                            logger.debug("Parallel execution completed successfully")
                        return result
                    except WorkerError as e:
                        # Handle WorkerError specially
                        try:
                            # If it's a WorkerError, extract and re-raise the original exception
                            # if available, otherwise re-raise the WorkerError itself
                            if (
                                isinstance(e, WorkerError)
                                and e.original_exception is not None
                            ):
                                if use_debug:
                                    logger.debug(
                                        f"Re-raising original exception from worker: {e.original_exception}"
                                    )
                                raise e.original_exception from e
                            else:
                                # If no original exception, raise the WorkerError itself
                                raise
                        except Exception as e:
                            # Provide more context for general errors
                            error_msg = f"Failed to handle WorkerError: {e}"
                            logger.error(error_msg)
                            if use_debug:
                                logger.debug(f"Traceback: {traceback.format_exc()}")
                            raise RuntimeError(error_msg) from e
                    except KeyboardInterrupt:
                        # Re-raise KeyboardInterrupt to allow proper cleanup
                        if use_debug:
                            logger.debug("KeyboardInterrupt detected during execution")
                        raise
                    except Exception as e:
                        # Provide more context for general errors
                        error_msg = f"Failed to execute parallel operation: {e}"
                        logger.error(error_msg)
                        if use_debug:
                            logger.debug(f"Traceback: {traceback.format_exc()}")
                        raise RuntimeError(error_msg) from e
            except KeyboardInterrupt:
                if use_debug:
                    logger.debug(
                        "KeyboardInterrupt detected during pool creation/usage"
                    )
                raise  # Re-raise to allow proper handling at higher level
            except Exception as e:
                error_msg = f"Failed to create or use pool: {e}"
                logger.error(error_msg)
                if use_debug:
                    logger.debug(f"Traceback: {traceback.format_exc()}")
                raise RuntimeError(error_msg) from e

        return wrapper

    return decorator


# Pre-configured decorators for common mapping operations
def pmap(func: Callable[[T], U]) -> Callable[[Iterator[T]], Iterator[U]]:
    """
    Decorator for parallel mapping using a process pool.

    This is a convenience wrapper around mmap('map') that applies the decorated
    function to each item in the input iterable in parallel using a process pool.
    It's optimized for CPU-bound operations that benefit from bypassing the GIL.

    Args:
        func: The function to parallelize.

    Returns:
        A wrapped function that, when called with an iterable, applies the original
        function to each item in parallel and returns the results.

    Example:
        >>> @pmap
        ... def square(x: int) -> int:
        ...     return x * x
        >>>
        >>> results = list(square(range(5)))
        >>> print(results)
        [0, 1, 4, 9, 16]
    """
    return mmap("map")(func)


def imap(func: Callable[[T], U]) -> Callable[[Iterator[T]], Iterator[U]]:
    """
    Decorator for iterative parallel mapping using a process pool.

    This is a convenience wrapper around mmap('imap') that applies the decorated
    function to each item in the input iterable in parallel using a process pool,
    but returns results as they become available rather than waiting for all to complete.
    This can be more memory-efficient for large datasets as it doesn't need to store
    all results in memory at once.

    Args:
        func: The function to parallelize.

    Returns:
        A wrapped function that, when called with an iterable, applies the original
        function to each item in parallel and returns an iterator of results.

    Example:
        >>> @imap
        ... def square(x: int) -> int:
        ...     return x * x
        >>>
        >>> for result in square(range(5)):
        ...     print(result)
        0
        1
        4
        9
        16
    """
    return mmap("imap")(func)


def amap(func: Callable[[T], U]) -> Callable[[Iterator[T]], Any]:
    """
    Decorator for asynchronous parallel mapping using a process pool.

    This is a convenience wrapper around mmap('amap', get_result=True) that applies
    the decorated function to each item in the input iterable in parallel using a
    process pool, and returns a future-like object. The results are automatically
    retrieved by calling .get() on the future.

    This is useful when you want to start a computation and then do other work
    before collecting the results.

    Args:
        func: The function to parallelize.

    Returns:
        A wrapped function that, when called with an iterable, applies the original
        function to each item in parallel and returns the results.

    Example:
        >>> @amap
        ... def square(x: int) -> int:
        ...     return x * x
        >>>
        >>> # This starts the computation and immediately returns a result object
        >>> result = square(range(5))
        >>> # Do other work here...
        >>> # Then get the results (already computed in parallel)
        >>> print(result)
        [0, 1, 4, 9, 16]
    """
    return mmap("amap", get_result=True)(func)

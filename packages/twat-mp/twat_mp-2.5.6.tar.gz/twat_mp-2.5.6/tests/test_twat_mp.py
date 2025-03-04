"""Test suite for twat_mp."""

import time
from typing import TypeVar, List
from unittest.mock import patch, MagicMock

import pytest
from twat_mp import ProcessPool, ThreadPool, amap, imap, mmap, pmap, set_debug_mode
from twat_mp.__version__ import version as __version__
from twat_mp.mp import WorkerError

T = TypeVar("T")
U = TypeVar("U")

# Test constants
TEST_PROCESS_POOL_SIZE = 2
TEST_THREAD_POOL_SIZE = 3


def test_version():
    """Verify package exposes version."""
    assert __version__


def _square(x: int) -> int:
    """Square a number."""
    return x * x


def _subs(x: int) -> int:
    """Subtract one."""
    return x - 1


# Create decorated versions of the functions
isquare = amap(_square)
isubs = amap(_subs)


def test_process_pool_context():
    """Test ProcessPool context manager functionality."""
    with ProcessPool() as pool:
        result = list(pool.map(_square, iter(range(5))))
        assert result == [0, 1, 4, 9, 16]


def test_thread_pool_context():
    """Test ThreadPool context manager functionality."""
    with ThreadPool() as pool:
        result = list(pool.map(_square, iter(range(5))))
        assert result == [0, 1, 4, 9, 16]


def test_amap_decorator():
    """Test amap decorator functionality."""
    result = isquare(iter(range(5)))
    assert result == [0, 1, 4, 9, 16]


def test_pmap_decorator():
    """Test pmap decorator functionality."""

    @pmap
    def square(x: int) -> int:
        return x * x

    result = list(square(iter(range(5))))
    assert result == [0, 1, 4, 9, 16]


def test_imap_decorator():
    """Test imap decorator functionality."""

    @imap
    def square(x: int) -> int:
        return x * x

    result = list(square(iter(range(5))))
    assert result == [0, 1, 4, 9, 16]

    # Test that imap returns an iterator
    iterator = square(iter(range(3)))
    assert next(iterator) == 0
    assert next(iterator) == 1
    assert next(iterator) == 4


def test_composed_operations():
    """Test composing multiple parallel operations."""
    result = list(isubs(isquare(iter(range(5)))))
    assert result == [-1, 0, 3, 8, 15]


def test_pool_nodes_specification():
    """Test specifying the number of nodes for a pool."""
    with ProcessPool(nodes=TEST_PROCESS_POOL_SIZE) as pool:
        assert pool.nodes == TEST_PROCESS_POOL_SIZE

    with ThreadPool(nodes=TEST_THREAD_POOL_SIZE) as pool:
        assert pool.nodes == TEST_THREAD_POOL_SIZE


@pytest.mark.benchmark
def test_parallel_vs_sequential_performance():
    """Benchmark parallel vs sequential performance."""

    # Define a CPU-intensive operation
    def slow_square(x: int) -> int:
        """A deliberately slow squaring function."""
        time.sleep(0.01)  # Simulate CPU work
        return x * x

    # Sequential execution
    start_time = time.time()
    sequential_result = [slow_square(x) for x in range(20)]
    sequential_time = time.time() - start_time

    # Parallel execution
    start_time = time.time()
    with ProcessPool() as pool:
        parallel_result = list(pool.map(slow_square, iter(range(20))))
    parallel_time = time.time() - start_time

    # Verify results are the same
    assert sequential_result == parallel_result

    # Parallel should be faster, but don't enforce it in tests
    # as it depends on the system and could cause flaky tests
    print(f"Sequential: {sequential_time:.4f}s, Parallel: {parallel_time:.4f}s")


def test_mmap_decorator_variants():
    """Test different variants of the mmap decorator."""
    # Test with map
    map_decorator = mmap("map")

    @map_decorator
    def square1(x: int) -> int:
        return x * x

    assert list(square1(iter(range(5)))) == [0, 1, 4, 9, 16]

    # Test with imap
    imap_decorator = mmap("imap")

    @imap_decorator
    def square2(x: int) -> int:
        return x * x

    assert list(square2(iter(range(5)))) == [0, 1, 4, 9, 16]

    # Test with amap and get_result=True
    amap_decorator = mmap("amap", get_result=True)

    @amap_decorator
    def square3(x: int) -> int:
        return x * x

    assert square3(iter(range(5))) == [0, 1, 4, 9, 16]


def test_empty_iterable():
    """Test handling of empty iterables."""
    # Test with ProcessPool
    with ProcessPool() as pool:
        result = list(pool.map(_square, iter([])))
        assert result == []

    # Test with ThreadPool
    with ThreadPool() as pool:
        result = list(pool.map(_square, iter([])))
        assert result == []

    # Test with decorators
    @pmap
    def square(x: int) -> int:
        return x * x

    assert list(square(iter([]))) == []

    @imap
    def square_imap(x: int) -> int:
        return x * x

    assert list(square_imap(iter([]))) == []

    @amap
    def square_amap(x: int) -> int:
        return x * x

    assert square_amap(iter([])) == []


def test_error_propagation():
    """Test that errors in worker functions are properly propagated."""

    def error_func(x: int) -> int:
        if x == 3:
            raise ValueError("Test error")
        return x * x

    # Test with ProcessPool - now expecting WorkerError
    with pytest.raises(WorkerError) as excinfo:
        with ProcessPool() as pool:
            list(pool.map(error_func, iter(range(5))))

    # Verify the original exception is stored in the WorkerError
    assert isinstance(excinfo.value.original_exception, ValueError)
    assert str(excinfo.value.original_exception) == "Test error"
    assert excinfo.value.input_item == 3

    # Test with ThreadPool - now expecting WorkerError
    with pytest.raises(WorkerError) as excinfo:
        with ThreadPool() as pool:
            list(pool.map(error_func, iter(range(5))))

    assert isinstance(excinfo.value.original_exception, ValueError)
    assert str(excinfo.value.original_exception) == "Test error"
    assert excinfo.value.input_item == 3

    # Test with decorators - these should re-raise the original exception
    @pmap
    def error_map(x: int) -> int:
        if x == 3:
            raise ValueError("Test error in pmap")
        return x * x

    with pytest.raises(ValueError, match="Test error in pmap"):
        list(error_map(iter(range(5))))

    @imap
    def error_imap(x: int) -> int:
        if x == 3:
            raise ValueError("Test error in imap")
        return x * x

    with pytest.raises(ValueError, match="Test error in imap"):
        list(error_imap(iter(range(5))))

    @amap
    def error_amap(x: int) -> int:
        if x == 3:
            raise ValueError("Test error in amap")
        return x * x

    with pytest.raises(ValueError, match="Test error in amap"):
        error_amap(iter(range(5)))


def test_debug_mode():
    """Test debug mode functionality."""
    # Enable debug mode
    with patch("logging.Logger.debug") as mock_debug:
        set_debug_mode(True)

        # Use a pool with debug mode
        with ProcessPool() as pool:
            list(pool.map(_square, iter(range(3))))

        # Verify debug logs were called
        assert mock_debug.called

        # Disable debug mode
        set_debug_mode(False)


def test_invalid_mapping_method():
    """Test that invalid mapping methods raise appropriate errors."""
    with pytest.raises(ValueError, match="Invalid mapping method"):
        mmap("invalid_method")

    # Test with a valid method but invalid pool attribute
    # We need to modify this test since we now validate methods early
    valid_method = "map"
    with patch("twat_mp.mp.MultiPool.__enter__") as mock_enter:
        # Create a mock pool without the requested method
        mock_pool = MagicMock()
        delattr(mock_pool, valid_method)  # Remove the valid method from the mock
        mock_enter.return_value = mock_pool

        decorator = mmap(valid_method)

        @decorator
        def test_func(x: int) -> int:
            return x * x

        with pytest.raises(AttributeError):
            test_func(iter(range(5)))


def test_pool_creation_failure():
    """Test handling of pool creation failures."""
    # We need to patch MultiPool.__enter__ instead of pathos.pools.ProcessPool
    with patch(
        "twat_mp.mp.MultiPool.__enter__",
        side_effect=RuntimeError("Test pool creation error"),
    ):
        with pytest.raises(RuntimeError, match="Test pool creation error"):
            with ProcessPool():
                pass


def test_resource_cleanup_after_exception():
    """Test that resources are properly cleaned up after an exception."""

    class TestError(Exception):
        """Custom exception for testing."""

        pass

    # Mock the pool to track cleanup calls
    with patch("twat_mp.mp.MultiPool.__exit__") as mock_exit:
        try:
            with ProcessPool():
                raise TestError("Test exception")
        except TestError:
            pass

        # Verify __exit__ was called
        assert mock_exit.called


def test_keyboard_interrupt_handling():
    """Test handling of KeyboardInterrupt."""
    # Mock the pool's terminate method to verify it's called
    with patch("pathos.pools.ProcessPool.terminate") as mock_terminate:
        with patch("pathos.pools.ProcessPool.join") as mock_join:
            try:
                with ProcessPool():
                    raise KeyboardInterrupt()
            except KeyboardInterrupt:
                pass

            # Verify terminate and join were called
            assert mock_terminate.called
            assert mock_join.called


def test_large_data_handling():
    """Test handling of large datasets."""
    # Create a large dataset (but not too large for tests)
    large_data = list(range(1000))

    # Process with ProcessPool
    with ProcessPool() as pool:
        result = list(pool.map(_square, iter(large_data)))
        assert len(result) == 1000
        assert result[0] == 0
        assert result[999] == 999 * 999

    # Process with ThreadPool
    with ThreadPool() as pool:
        result = list(pool.map(_square, iter(large_data)))
        assert len(result) == 1000
        assert result[0] == 0
        assert result[999] == 999 * 999


def test_nested_pools():
    """Test nested pool usage."""

    def nested_pool_func(x: int) -> List[int]:
        # Create a nested pool inside a worker function
        with ThreadPool(nodes=2) as inner_pool:
            # Square each number from 0 to x
            return list(inner_pool.map(_square, iter(range(x + 1))))

    # Use an outer pool to process items
    with ProcessPool(nodes=2) as outer_pool:
        results = list(outer_pool.map(nested_pool_func, iter(range(3))))

    # Verify results
    assert results == [
        [0],  # nested_pool_func(0) -> [0²]
        [0, 1],  # nested_pool_func(1) -> [0², 1²]
        [0, 1, 4],  # nested_pool_func(2) -> [0², 1², 2²]
    ]


def test_pool_reuse_failure():
    """Test that attempting to reuse a closed pool raises an appropriate error."""
    pool = None

    # Create and use a pool
    with ProcessPool() as p:
        pool = p
        list(p.map(_square, iter(range(5))))

    # Attempt to reuse the pool outside its context
    # Since we're now patching the map method, we need to test differently
    if pool is not None:
        # The pool's map method should be our enhanced version that checks if the pool is None
        with pytest.raises(RuntimeError, match="Pool not initialized"):
            # This should fail because the pool is closed and cleared in __exit__
            pool.map(_square, iter(range(5)))


def test_custom_exception_handling():
    """Test handling of custom exceptions in worker functions."""

    class CustomError(Exception):
        """Custom exception for testing."""

        pass

    def raise_custom_error(x: int) -> int:
        if x > 2:
            raise CustomError(f"Value {x} is too large")
        return x

    # Test with ProcessPool - now expecting WorkerError
    with pytest.raises(WorkerError) as excinfo:
        with ProcessPool() as pool:
            list(pool.map(raise_custom_error, iter(range(5))))

    # Verify the original exception is stored in the WorkerError
    assert isinstance(excinfo.value.original_exception, CustomError)
    assert str(excinfo.value.original_exception) == "Value 3 is too large"
    assert excinfo.value.input_item == 3

    # Test with decorator - should re-raise the original exception
    @pmap
    def decorated_error_func(x: int) -> int:
        if x > 2:
            raise CustomError(f"Decorated value {x} is too large")
        return x

    with pytest.raises(CustomError, match="Decorated value 3 is too large"):
        list(decorated_error_func(iter(range(5))))

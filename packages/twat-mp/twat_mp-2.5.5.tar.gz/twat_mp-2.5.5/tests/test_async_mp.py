#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["pytest", "pytest-asyncio", "aiomultiprocess"]
# ///
# this_file: tests/test_async_mp.py

"""
Tests for the async multiprocessing functionality.
"""

import asyncio
from typing import Any

import pytest

from twat_mp import AsyncMultiPool, apmap


async def async_double(x: int) -> int:
    """Simple async function that doubles its input."""
    await asyncio.sleep(0.01)  # Simulate some async work
    return x * 2


async def async_raise_error(x: Any) -> Any:
    """Async function that raises an error."""
    raise ValueError(f"Error processing {x}")


@pytest.mark.asyncio
async def test_async_multi_pool_map() -> None:
    """Test basic mapping functionality."""
    async with AsyncMultiPool() as pool:
        results = await pool.map(async_double, range(5))
    assert results == [0, 2, 4, 6, 8]


@pytest.mark.asyncio
async def test_async_multi_pool_empty() -> None:
    """Test mapping with empty iterable."""
    async with AsyncMultiPool() as pool:
        results = await pool.map(async_double, [])
    assert results == []


@pytest.mark.asyncio
async def test_async_multi_pool_error() -> None:
    """Test error handling in pool."""
    with pytest.raises(ValueError):
        async with AsyncMultiPool() as pool:
            await pool.map(async_raise_error, range(5))


@pytest.mark.asyncio
async def test_async_multi_pool_imap() -> None:
    """Test imap functionality."""
    async with AsyncMultiPool() as pool:
        results = []
        async for result in pool.imap(async_double, range(5)):
            results.append(result)
    assert results == [0, 2, 4, 6, 8]


@pytest.mark.asyncio
async def test_async_multi_pool_starmap() -> None:
    """Test starmap functionality."""

    async def async_sum(*args: int) -> int:
        await asyncio.sleep(0.01)
        return sum(args)

    async with AsyncMultiPool() as pool:
        results = await pool.starmap(async_sum, [(1, 2), (3, 4), (5, 6)])
    assert results == [3, 7, 11]


@pytest.mark.asyncio
async def test_apmap_decorator() -> None:
    """Test the apmap decorator."""

    @apmap
    async def double(x: int) -> int:
        await asyncio.sleep(0.01)
        return x * 2

    results = await double(range(5))
    assert results == [0, 2, 4, 6, 8]


@pytest.mark.asyncio
async def test_pool_not_initialized() -> None:
    """Test error when using pool methods without initialization."""
    pool = AsyncMultiPool()
    with pytest.raises(RuntimeError, match="Pool not initialized"):
        await pool.map(async_double, range(5))


@pytest.mark.asyncio
async def test_pool_cleanup() -> None:
    """Test that pool is properly cleaned up after use."""
    pool = AsyncMultiPool()
    async with pool:
        assert pool.pool is not None
        await pool.map(async_double, range(5))
    assert pool.pool is None

#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "pytest",
#   "pytest-asyncio",
#   "loguru",
#   "diskcache",
#   "joblib",
#   "types-pytest",
#   "cachetools",
#   "cachebox",
#   "klepto",
#   "aiocache",
# ]
# ///
# this_file: tests/test_decorators.py

"""Tests for the cache decorators."""

import asyncio
import time
from typing import Any

import pytest
import importlib.util

from twat_cache.decorators import mcache, bcache, fcache, ucache, acache
from tests.test_constants import (
    CACHE_SIZE,
    CACHE_TTL,
    EXPECTED_CALLS_SINGLE,
    EXPECTED_CALLS_DOUBLE,
    EXPECTED_CALLS_TRIPLE,
    EXPECTED_CALLS_QUAD,
    SQUARE_INPUT,
    SQUARE_RESULT,
    TEST_KEY,
    TEST_BOOL,
    TEST_INT,
    TEST_VALUE,
    TEST_RESULT,
    TEST_FOLDER,
)

# Check optional backend availability
HAS_AIOCACHE = bool(importlib.util.find_spec("aiocache"))
HAS_CACHEBOX = bool(importlib.util.find_spec("cachebox"))
HAS_CACHETOOLS = bool(importlib.util.find_spec("cachetools"))
HAS_DISKCACHE = bool(importlib.util.find_spec("diskcache"))
HAS_JOBLIB = bool(importlib.util.find_spec("joblib"))
HAS_KLEPTO = bool(importlib.util.find_spec("klepto"))


def test_basic_memory_cache():
    """Test basic memory caching with functools."""
    call_count = 0

    @bcache()
    def square(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * x

    # First call should compute
    result1 = square(TEST_VALUE)
    assert result1 == TEST_RESULT
    assert call_count == EXPECTED_CALLS_SINGLE

    # Second call should use cache
    result2 = square(TEST_VALUE)
    assert result2 == TEST_RESULT
    assert call_count == EXPECTED_CALLS_SINGLE


@pytest.mark.skipif(not HAS_CACHEBOX, reason="cachebox not available")
def test_cachebox_memory():
    """Test memory caching with cachebox."""
    call_count = 0

    @bcache(engine="cachebox")
    def square(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * x

    # First call should compute
    result1 = square(TEST_VALUE)
    assert result1 == TEST_RESULT
    assert call_count == EXPECTED_CALLS_SINGLE

    # Second call should use cache
    result2 = square(TEST_VALUE)
    assert result2 == TEST_RESULT
    assert call_count == EXPECTED_CALLS_SINGLE


@pytest.mark.skipif(not HAS_CACHETOOLS, reason="cachetools not available")
def test_cachetools_memory():
    """Test memory caching with cachetools."""
    call_count = 0

    @bcache(engine="cachetools")
    def square(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * x

    # First call should compute
    result1 = square(TEST_VALUE)
    assert result1 == TEST_RESULT
    assert call_count == EXPECTED_CALLS_SINGLE

    # Second call should use cache
    result2 = square(TEST_VALUE)
    assert result2 == TEST_RESULT
    assert call_count == EXPECTED_CALLS_SINGLE


@pytest.mark.skipif(not HAS_DISKCACHE, reason="diskcache not available")
def test_diskcache_basic():
    """Test basic disk caching with diskcache."""
    call_count = 0

    @bcache(engine="diskcache", folder_name=TEST_FOLDER)
    def square(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * x

    # First call should compute
    result1 = square(TEST_VALUE)
    assert result1 == TEST_RESULT
    assert call_count == EXPECTED_CALLS_SINGLE

    # Second call should use cache
    result2 = square(TEST_VALUE)
    assert result2 == TEST_RESULT
    assert call_count == EXPECTED_CALLS_SINGLE


@pytest.mark.skipif(not HAS_KLEPTO, reason="klepto not available")
def test_klepto_sql():
    """Test basic disk caching with klepto SQL backend."""
    call_count = 0

    @bcache(engine="klepto", folder_name=TEST_FOLDER)
    def square(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * x

    # First call should compute
    result1 = square(TEST_VALUE)
    assert result1 == TEST_RESULT
    assert call_count == EXPECTED_CALLS_SINGLE

    # Second call should use cache
    result2 = square(TEST_VALUE)
    assert result2 == TEST_RESULT
    assert call_count == EXPECTED_CALLS_SINGLE


@pytest.mark.skipif(not HAS_JOBLIB, reason="joblib not available")
def test_joblib_file():
    """Test file-based caching with joblib."""
    call_count = 0

    @bcache(engine="joblib", folder_name=TEST_FOLDER)
    def square(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * x

    # First call should compute
    result1 = square(TEST_VALUE)
    assert result1 == TEST_RESULT
    assert call_count == EXPECTED_CALLS_SINGLE

    # Second call should use cache
    result2 = square(TEST_VALUE)
    assert result2 == TEST_RESULT
    assert call_count == EXPECTED_CALLS_SINGLE


@pytest.mark.skipif(not HAS_KLEPTO, reason="klepto not available")
def test_klepto_file():
    """Test file-based caching with klepto file backend."""
    call_count = 0

    @bcache(engine="klepto", folder_name=TEST_FOLDER)
    def square(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * x

    # First call should compute
    result1 = square(TEST_VALUE)
    assert result1 == TEST_RESULT
    assert call_count == EXPECTED_CALLS_SINGLE

    # Second call should use cache
    result2 = square(TEST_VALUE)
    assert result2 == TEST_RESULT
    assert call_count == EXPECTED_CALLS_SINGLE


@pytest.mark.skipif(not HAS_AIOCACHE, reason="aiocache not available")
def test_aiocache_memory():
    """Test async caching with aiocache."""
    call_count = 0

    @ucache(engine="aiocache")
    async def square(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * x

    # First call should compute
    result1 = square(TEST_VALUE)
    assert result1 == TEST_RESULT
    assert call_count == EXPECTED_CALLS_SINGLE

    # Second call should use cache
    result2 = square(TEST_VALUE)
    assert result2 == TEST_RESULT
    assert call_count == EXPECTED_CALLS_SINGLE


def test_memory_cache_cachebox() -> None:
    """Test memory caching with cachebox (if available)."""
    try:
        import cachebox

    except ImportError:
        pytest.skip("cachebox not available")

    call_count = 0

    @mcache(maxsize=CACHE_SIZE)
    def expensive_func(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * x

    # First calls
    expensive_func(1)
    expensive_func(2)
    assert call_count == EXPECTED_CALLS_DOUBLE

    # Should still be cached
    expensive_func(1)
    expensive_func(2)
    assert call_count == EXPECTED_CALLS_DOUBLE

    # Should evict oldest entry
    expensive_func(3)
    assert call_count == EXPECTED_CALLS_TRIPLE
    expensive_func(1)  # Should recompute
    assert call_count == EXPECTED_CALLS_QUAD


def test_memory_cache_cachetools() -> None:
    """Test memory caching with cachetools (if available)."""
    try:
        import cachetools

    except ImportError:
        pytest.skip("cachetools not available")

    call_count = 0

    @mcache(maxsize=CACHE_SIZE)
    def expensive_func(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * x

    # Test caching behavior
    assert expensive_func(SQUARE_INPUT) == SQUARE_RESULT
    assert expensive_func(SQUARE_INPUT) == SQUARE_RESULT
    assert call_count == EXPECTED_CALLS_SINGLE


def test_basic_disk_cache() -> None:
    """Test basic disk caching with diskcache."""
    try:
        import diskcache

    except ImportError:
        pytest.skip("diskcache not available")

    call_count = 0

    @bcache(maxsize=CACHE_SIZE)
    def expensive_func(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * x

    # Test caching behavior
    assert expensive_func(SQUARE_INPUT) == SQUARE_RESULT
    assert expensive_func(SQUARE_INPUT) == SQUARE_RESULT
    assert call_count == EXPECTED_CALLS_SINGLE


def test_basic_disk_cache_sql() -> None:
    """Test basic disk caching with klepto SQL backend."""
    try:
        import klepto

    except ImportError:
        pytest.skip("klepto not available")

    call_count = 0

    @bcache(maxsize=CACHE_SIZE, use_sql=True)
    def expensive_func(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * x

    # Test caching behavior
    assert expensive_func(SQUARE_INPUT) == SQUARE_RESULT
    assert expensive_func(SQUARE_INPUT) == SQUARE_RESULT
    assert call_count == EXPECTED_CALLS_SINGLE


def test_file_cache_joblib() -> None:
    """Test file-based caching with joblib."""
    try:
        import joblib

    except ImportError:
        pytest.skip("joblib not available")

    call_count = 0

    @fcache(maxsize=CACHE_SIZE)
    def expensive_func(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * x

    # Test caching behavior
    assert expensive_func(SQUARE_INPUT) == SQUARE_RESULT
    assert expensive_func(SQUARE_INPUT) == SQUARE_RESULT
    assert call_count == EXPECTED_CALLS_SINGLE


def test_file_cache_klepto() -> None:
    """Test file-based caching with klepto file backend."""
    try:
        import klepto

    except ImportError:
        pytest.skip("klepto not available")

    call_count = 0

    @fcache(maxsize=CACHE_SIZE)
    def expensive_func(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * x

    # Test caching behavior
    assert expensive_func(SQUARE_INPUT) == SQUARE_RESULT
    assert expensive_func(SQUARE_INPUT) == SQUARE_RESULT
    assert call_count == EXPECTED_CALLS_SINGLE


def test_universal_cache() -> None:
    """Test universal caching with automatic backend selection."""
    call_count = 0

    @ucache(maxsize=CACHE_SIZE)
    def expensive_func(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * x

    # Test caching behavior
    assert expensive_func(SQUARE_INPUT) == SQUARE_RESULT
    assert expensive_func(SQUARE_INPUT) == SQUARE_RESULT
    assert call_count == EXPECTED_CALLS_SINGLE


async def test_async_cache() -> None:
    """Test async caching with aiocache."""
    try:
        import aiocache

    except ImportError:
        pytest.skip("aiocache not available")

    call_count = 0

    @acache(maxsize=CACHE_SIZE)
    async def expensive_func(x: int) -> int:
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0.1)
        return x * x

    # Test caching behavior
    result1 = await expensive_func(SQUARE_INPUT)
    assert result1 == SQUARE_RESULT

    result2 = await expensive_func(SQUARE_INPUT)
    assert result2 == SQUARE_RESULT
    assert call_count == EXPECTED_CALLS_SINGLE


def test_key_generation() -> None:
    """Test cache key generation."""
    call_count = 0

    @mcache()
    def test_func(x: Any) -> str:
        nonlocal call_count
        call_count += 1
        return str(x)

    # Test with different types
    test_func(TEST_KEY)
    test_func(TEST_BOOL)
    test_func(TEST_INT)
    assert call_count == EXPECTED_CALLS_TRIPLE

    # Test with same values
    test_func(TEST_KEY)
    test_func(TEST_BOOL)
    test_func(TEST_INT)
    assert call_count == EXPECTED_CALLS_TRIPLE  # Should use cache


def test_ttl_cache() -> None:
    """Test time-to-live cache behavior."""
    call_count = 0

    @mcache(ttl=CACHE_TTL)
    def expensive_func(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * x

    # First call
    assert expensive_func(SQUARE_INPUT) == SQUARE_RESULT
    assert call_count == EXPECTED_CALLS_SINGLE

    # Should still be cached
    assert expensive_func(SQUARE_INPUT) == SQUARE_RESULT
    assert call_count == EXPECTED_CALLS_SINGLE

    # Wait for TTL to expire
    time.sleep(CACHE_TTL + 0.1)

    # Should recompute
    assert expensive_func(SQUARE_INPUT) == SQUARE_RESULT
    assert call_count == EXPECTED_CALLS_DOUBLE

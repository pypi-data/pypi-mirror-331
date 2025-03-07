#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "pytest",
#   "pydantic",
#   "pydantic-settings",
# ]
# ///
# this_file: tests/test_engines.py

"""Tests for cache engine implementations."""

from typing import Any

import pytest

from twat_cache.engines.base import CacheEngine
from twat_cache.engines.functools import FunctoolsCacheEngine
from twat_cache.engines.manager import EngineManager
from twat_cache.config import create_cache_config, CacheConfig
from .test_constants import (
    CACHE_SIZE,
    CACHE_TTL,
    EXPECTED_CALLS_SINGLE,
    SQUARE_INPUT,
    SQUARE_RESULT,
    TEST_KEY,
    TEST_BOOL,
    TEST_INT,
    TEST_LIST,
)

# Test constants
TEST_VALUE = "test_value"
TEST_FOLDER = "test_cache"
TEST_FUNCTION_RESULT = 42


@pytest.fixture
def engine_manager() -> EngineManager:
    """Provide a clean engine manager instance."""
    return EngineManager()


@pytest.fixture
def base_config() -> CacheConfig:
    """Provide a basic cache configuration."""
    return create_cache_config(maxsize=CACHE_SIZE)


@pytest.fixture
def base_engine(base_config: CacheConfig) -> CacheEngine[Any, Any]:
    """Provide a basic cache engine instance."""
    return FunctoolsCacheEngine(base_config)


def create_test_engine() -> CacheEngine:
    """Create a test cache engine instance."""
    config = CacheConfig(
        maxsize=CACHE_SIZE,
        ttl=CACHE_TTL,
        folder_name="test",
        secure=True,
    )
    return FunctoolsCacheEngine(config)


def test_engine_initialization() -> None:
    """Test cache engine initialization."""
    engine = create_test_engine()
    assert isinstance(engine, CacheEngine)
    assert engine.config.maxsize == CACHE_SIZE
    assert engine.config.ttl == CACHE_TTL


def test_key_generation() -> None:
    """Test cache key generation."""
    engine = create_test_engine()

    # Test with different types
    assert isinstance(engine._make_key(TEST_KEY), str)
    assert isinstance(engine._make_key(TEST_INT), str)
    assert isinstance(engine._make_key(TEST_BOOL), str)

    # Test with complex types
    assert isinstance(engine._make_key(TEST_LIST), str)
    assert isinstance(engine._make_key((1, 2, 3)), str)
    assert isinstance(engine._make_key({"a": 1}), str)


def test_cache_operations() -> None:
    """Test basic cache operations."""
    create_test_engine()
    call_count = 0

    def test_function(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * x

    # First call
    result = test_function(SQUARE_INPUT)
    assert result == SQUARE_RESULT
    assert call_count == EXPECTED_CALLS_SINGLE

    # Second call (should use cache)
    result = test_function(SQUARE_INPUT)
    assert result == SQUARE_RESULT
    assert call_count == EXPECTED_CALLS_SINGLE  # Should not increment


def test_cache_eviction() -> None:
    """Test cache eviction behavior."""
    engine = create_test_engine()

    # Fill cache
    for i in range(CACHE_SIZE + 1):
        engine.set(str(i), i)

    # Check eviction
    assert len(engine._cache) <= CACHE_SIZE


def test_cache_ttl() -> None:
    """Test time-to-live behavior."""
    import time

    create_test_engine()
    call_count = 0

    def test_function(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * x

    # First call
    result = test_function(SQUARE_INPUT)
    assert result == SQUARE_RESULT
    assert call_count == EXPECTED_CALLS_SINGLE

    # Wait for TTL to expire
    time.sleep(CACHE_TTL + 0.1)

    # Should recompute
    result = test_function(SQUARE_INPUT)
    assert result == SQUARE_RESULT
    assert call_count == EXPECTED_CALLS_SINGLE + 1


def test_cache_clear() -> None:
    """Test cache clearing."""
    engine = create_test_engine()

    # Add some items
    for i in range(CACHE_SIZE):
        engine.set(str(i), i)

    # Clear cache
    engine.clear()
    assert len(engine._cache) == 0


def test_cache_stats() -> None:
    """Test cache statistics."""
    engine = create_test_engine()
    call_count = 0

    def test_function(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * x

    # First call (miss)
    result = test_function(SQUARE_INPUT)
    assert result == SQUARE_RESULT
    assert engine.stats["misses"] == 1

    # Second call (hit)
    result = test_function(SQUARE_INPUT)
    assert result == SQUARE_RESULT
    assert engine.stats["hits"] == 1

#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "pytest",
#   "pytest-asyncio",
#   "loguru",
# ]
# ///
# this_file: tests/test_twat_cache.py

"""Test suite for twat_cache core functionality.

This module contains comprehensive tests for all cache engine implementations,
focusing on the core _get, _set, and clear methods.
"""

from pathlib import Path
import pytest

from twat_cache.engines.functools import FunctoolsCacheEngine
from twat_cache.engines.cachebox import CacheBoxEngine
from twat_cache.engines.cachetools import CacheToolsEngine
from twat_cache.engines.diskcache import DiskCacheEngine
from twat_cache.engines.joblib import JoblibEngine
from twat_cache.engines.klepto import KleptoEngine
from twat_cache.engines.aiocache import AioCacheEngine
from twat_cache.type_defs import CacheConfig, CacheKey
from twat_cache.config import create_cache_config

try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


# Test configurations
@pytest.fixture
def base_config() -> CacheConfig:
    """Provide a basic cache configuration."""
    return create_cache_config(maxsize=100)


@pytest.fixture
def temp_path(tmp_path: Path) -> Path:
    """Provide a temporary directory for disk-based caches."""
    return tmp_path / "cache"


# LRU Cache Tests
@pytest.fixture
def lru_engine(base_config: CacheConfig) -> FunctoolsCacheEngine:
    """Create an LRU cache engine instance."""
    return FunctoolsCacheEngine(base_config)


def test_lru_cache_get_set(lru_engine: FunctoolsCacheEngine) -> None:
    """Test basic get/set operations for LRU cache."""
    key: CacheKey = "test_key"
    value = "test_value"

    # Test cache miss
    assert lru_engine._get_cached_value(key) is None

    # Test cache hit
    lru_engine._set_cached_value(key, value)
    assert lru_engine._get_cached_value(key) == value


def test_lru_cache_clear(lru_engine: FunctoolsCacheEngine) -> None:
    """Test clear operation for LRU cache."""
    key: CacheKey = "test_key"
    value = "test_value"

    lru_engine._set_cached_value(key, value)
    lru_engine.clear()
    assert lru_engine._get_cached_value(key) is None


def test_lru_cache_maxsize(lru_engine: FunctoolsCacheEngine) -> None:
    """Test maxsize enforcement for LRU cache."""
    for i in range(150):  # More than maxsize
        lru_engine._set_cached_value(f"key_{i}", f"value_{i}")

    # Oldest entries should be evicted
    assert lru_engine._get_cached_value("key_0") is None
    assert lru_engine._get_cached_value("key_149") is not None


# DiskCache Tests
@pytest.fixture
def disk_engine(base_config: CacheConfig, temp_path: Path) -> DiskCacheEngine:
    """Create a disk cache engine instance."""
    config = create_cache_config(maxsize=100, cache_dir=str(temp_path))
    return DiskCacheEngine(config)


def test_disk_cache_persistence(disk_engine: DiskCacheEngine) -> None:
    """Test persistence of disk cache."""
    key: CacheKey = "test_key"
    value = "test_value"

    disk_engine._set_cached_value(key, value)
    assert disk_engine._get_cached_value(key) == value

    # Create new instance with same path
    config = disk_engine.config
    new_engine = DiskCacheEngine(config)
    assert new_engine._get_cached_value(key) == value


# Joblib Tests
@pytest.fixture
def joblib_engine(base_config: CacheConfig, temp_path: Path) -> JoblibEngine:
    """Create a joblib cache engine instance."""
    config = create_cache_config(maxsize=100, cache_dir=str(temp_path))
    return JoblibEngine(config)


@pytest.mark.skipif(not HAS_NUMPY, reason="numpy not available")
def test_joblib_numpy_array(joblib_engine: JoblibEngine) -> None:
    """Test joblib cache with NumPy arrays."""
    key: CacheKey = "array_key"
    value = np.array([[1, 2], [3, 4]])

    joblib_engine._set_cached_value(key, value)
    cached = joblib_engine._get_cached_value(key)
    assert isinstance(cached, np.ndarray)
    assert np.array_equal(cached, value)


# Klepto Tests
@pytest.fixture
def klepto_engine(base_config: CacheConfig, temp_path: Path) -> KleptoEngine:
    """Create a klepto cache engine instance."""
    config = create_cache_config(maxsize=100, cache_dir=str(temp_path))
    return KleptoEngine(config)


def test_klepto_persistence(klepto_engine: KleptoEngine) -> None:
    """Test persistence of klepto cache."""
    key: CacheKey = "test_key"
    value = {"complex": "data", "nested": {"value": 42}}

    klepto_engine._set_cached_value(key, value)
    assert klepto_engine._get_cached_value(key) == value


# Async Cache Tests
@pytest.fixture
async def async_engine(base_config: CacheConfig) -> AioCacheEngine:
    """Create an async cache engine instance."""
    return AioCacheEngine(base_config)


@pytest.mark.asyncio
async def test_async_cache_operations(async_engine: AioCacheEngine) -> None:
    """Test async cache operations."""
    key: CacheKey = "test_key"
    value = "test_value"

    assert await async_engine._get_cached_value(key) is None
    await async_engine._set_cached_value(key, value)
    assert await async_engine._get_cached_value(key) == value

    await async_engine.clear()
    assert await async_engine._get_cached_value(key) is None


# CacheBox Tests
@pytest.fixture
def cachebox_engine(base_config: CacheConfig) -> CacheBoxEngine:
    """Create a cachebox engine instance."""
    return CacheBoxEngine(base_config)


def test_cachebox_operations(cachebox_engine: CacheBoxEngine) -> None:
    """Test basic operations for cachebox."""
    key: CacheKey = "test_key"
    value = "test_value"

    assert cachebox_engine._get_cached_value(key) is None
    cachebox_engine._set_cached_value(key, value)
    assert cachebox_engine._get_cached_value(key) == value

    cachebox_engine.clear()
    assert cachebox_engine._get_cached_value(key) is None


# CacheTools Tests
@pytest.fixture
def cachetools_engine(base_config: CacheConfig) -> CacheToolsEngine:
    """Create a cachetools engine instance."""
    return CacheToolsEngine(base_config)


def test_cachetools_operations(cachetools_engine: CacheToolsEngine) -> None:
    """Test basic operations for cachetools."""
    key: CacheKey = "test_key"
    value = "test_value"

    assert cachetools_engine._get_cached_value(key) is None
    cachetools_engine._set_cached_value(key, value)
    assert cachetools_engine._get_cached_value(key) == value

    cachetools_engine.clear()
    assert cachetools_engine._get_cached_value(key) is None


@pytest.fixture
def functools_engine(base_config: CacheConfig) -> FunctoolsCacheEngine:
    """Fixture for testing the functools cache engine."""
    return FunctoolsCacheEngine(base_config)


def test_functools_cache_get_set(functools_engine: FunctoolsCacheEngine) -> None:
    """Test basic get/set operations with the functools cache."""
    key: CacheKey = "test_key"
    value = "test_value"

    # Test cache miss
    assert functools_engine._get_cached_value(key) is None

    # Test cache hit
    functools_engine._set_cached_value(key, value)
    assert functools_engine._get_cached_value(key) == value


def test_functools_cache_clear(functools_engine: FunctoolsCacheEngine) -> None:
    """Test clearing the functools cache."""
    key: CacheKey = "test_key"
    value = "test_value"

    functools_engine._set_cached_value(key, value)
    functools_engine.clear()
    assert functools_engine._get_cached_value(key) is None


def test_functools_cache_maxsize(functools_engine: FunctoolsCacheEngine) -> None:
    """Test maxsize enforcement in functools cache."""
    for i in range(150):  # More than maxsize
        functools_engine._set_cached_value(f"key_{i}", f"value_{i}")

    # Oldest entries should be evicted
    assert functools_engine._get_cached_value("key_0") is None
    assert functools_engine._get_cached_value("key_149") is not None

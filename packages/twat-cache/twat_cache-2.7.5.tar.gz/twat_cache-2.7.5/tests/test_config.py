#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "pytest",
# ]
# ///
# this_file: tests/test_config.py

"""Tests for the configuration system."""

import pytest
from pydantic import ValidationError

from twat_cache.config import CacheConfig, create_cache_config
from tests.test_constants import (
    SMALL_CACHE_SIZE,
    DEFAULT_CACHE_SIZE,
    SHORT_TTL,
    DEFAULT_TTL,
    MIN_COMPRESSION,
    MAX_COMPRESSION,
    DEFAULT_COMPRESSION,
    DIR_PERMISSIONS,
    FILE_PERMISSIONS,
)


def test_cache_config_defaults():
    """Test default configuration values."""
    config = CacheConfig()
    assert config.maxsize is None
    assert config.folder_name is None
    assert config.ttl is None
    assert config.use_sql is False
    assert config.compress is False
    assert config.secure is True
    assert config.policy == "lru"
    assert config.backend is None


def test_cache_config_validation():
    """Test configuration validation."""
    # Test valid configurations
    config = create_cache_config(
        maxsize=DEFAULT_CACHE_SIZE,
        ttl=DEFAULT_TTL,
        compression_level=DEFAULT_COMPRESSION,
    )
    assert config.maxsize == DEFAULT_CACHE_SIZE
    assert config.ttl == DEFAULT_TTL
    assert config.compression_level == DEFAULT_COMPRESSION

    # Test invalid maxsize
    with pytest.raises(ValidationError):
        create_cache_config(maxsize=-1)

    # Test invalid TTL
    with pytest.raises(ValidationError):
        create_cache_config(ttl=-1)

    # Test invalid compression level
    with pytest.raises(ValidationError):
        create_cache_config(compression_level=MAX_COMPRESSION + 1)


def test_cache_config_permissions():
    """Test file permission settings."""
    config = create_cache_config(secure=True)
    assert config.dir_permissions == DIR_PERMISSIONS
    assert config.file_permissions == FILE_PERMISSIONS

    config = create_cache_config(secure=False)
    assert config.dir_permissions != DIR_PERMISSIONS
    assert config.file_permissions != FILE_PERMISSIONS


def test_cache_config_size_limits():
    """Test cache size limit validation."""
    # Small cache
    config = create_cache_config(maxsize=SMALL_CACHE_SIZE)
    assert config.maxsize == SMALL_CACHE_SIZE

    # Default cache
    config = create_cache_config(maxsize=DEFAULT_CACHE_SIZE)
    assert config.maxsize == DEFAULT_CACHE_SIZE

    # Unlimited cache
    config = create_cache_config(maxsize=None)
    assert config.maxsize is None


def test_cache_config_ttl():
    """Test TTL validation and handling."""
    # Short TTL
    config = create_cache_config(ttl=SHORT_TTL)
    assert config.ttl == SHORT_TTL

    # Default TTL
    config = create_cache_config(ttl=DEFAULT_TTL)
    assert config.ttl == DEFAULT_TTL

    # No TTL
    config = create_cache_config(ttl=None)
    assert config.ttl is None


def test_cache_config_compression():
    """Test compression settings validation."""
    # Min compression
    config = create_cache_config(compression_level=MIN_COMPRESSION)
    assert config.compression_level == MIN_COMPRESSION

    # Max compression
    config = create_cache_config(compression_level=MAX_COMPRESSION)
    assert config.compression_level == MAX_COMPRESSION

    # Default compression
    config = create_cache_config(compression_level=DEFAULT_COMPRESSION)
    assert config.compression_level == DEFAULT_COMPRESSION

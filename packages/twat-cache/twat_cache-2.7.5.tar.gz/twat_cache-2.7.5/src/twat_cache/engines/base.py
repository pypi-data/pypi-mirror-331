#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "loguru",
#   "pydantic",
# ]
# ///
# this_file: src/twat_cache/engines/base.py

"""
Base cache engine implementation.

This module provides the foundation for all cache backend implementations,
implementing common functionality and enforcing the CacheEngine protocol.
"""

from abc import ABC, abstractmethod
import time
from pathlib import Path
from typing import Any, Generic
from collections.abc import Callable
from importlib import util

from loguru import logger

from twat_cache.config import CacheConfig
from twat_cache.exceptions import (
    ConfigurationError,
    PathError,
)
from twat_cache.type_defs import CacheKey, P, R
from twat_cache.paths import get_cache_path, validate_cache_path
from twat_cache.engines.common import (
    ensure_dir_exists,
    create_cache_key,
)


def is_package_available(package_name: str) -> bool:
    """Check if a Python package is available.

    Args:
        package_name: Name of the package to check.

    Returns:
        bool: True if the package is available, False otherwise.
    """
    return util.find_spec(package_name) is not None


class BaseCacheEngine(ABC, Generic[P, R]):
    """
    Abstract base class for cache engine implementations.

    This class provides common functionality and enforces the CacheEngine protocol
    for all cache backend implementations.

    Args:
        config: Cache configuration object implementing CacheConfig protocol
    """

    def __init__(self, config: CacheConfig) -> None:
        """Initialize the cache engine with the given configuration."""
        self._config = config
        self._hits = 0
        self._misses = 0
        self._size = 0
        self._cache_path: Path | None = None
        self._cache: dict[CacheKey, tuple[R, float | None]] = {}
        self._last_access = 0.0
        self._last_update = 0.0
        self._created_at = time.time()

        # Validate configuration
        self.validate_config()

        # Initialize cache path if needed
        if self._config.folder_name is not None:
            try:
                self._cache_path = get_cache_path(self._config.folder_name)

                # Ensure directory exists with proper permissions
                if self._cache_path:
                    ensure_dir_exists(self._cache_path, mode=0o700 if self._config.secure else 0o755)

            except (OSError, PermissionError) as e:
                logger.error(f"Failed to initialize cache path: {e}")
                msg = f"Failed to initialize cache path: {e!s}"
                raise PathError(msg) from e

        logger.debug(f"Initialized {self.__class__.__name__} with config: {config}")

    @property
    def stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "hits": self._hits,
            "misses": self._misses,
            "size": self._size,
            "maxsize": self._config.maxsize,
            "backend": self.__class__.__name__,
            "path": str(self._cache_path) if self._cache_path else None,
            "policy": self._config.policy,
            "ttl": self._config.ttl,
            "last_access": self._last_access,
            "last_update": self._last_update,
            "created_at": self._created_at,
            "uptime": time.time() - self._created_at,
        }

    def validate_config(self) -> None:
        """
        Validate the engine configuration.

        Raises:
            ConfigurationError: If the configuration is invalid
        """
        # Check for folder existence if provided
        if self._config.folder_name is not None:
            try:
                validate_cache_path(self._config.folder_name)
            except ValueError as e:
                logger.error(f"Invalid cache folder configuration: {e}")
                msg = f"Invalid cache folder: {e!s}"
                raise ConfigurationError(msg) from e

        # Check TTL is non-negative if provided
        if self._config.ttl is not None and self._config.ttl < 0:
            msg = f"TTL must be a non-negative number, got {self._config.ttl}"
            logger.error(msg)
            raise ConfigurationError(msg)

        # Check maxsize is positive if provided
        if self._config.maxsize is not None and self._config.maxsize <= 0:
            msg = f"Cache maxsize must be a positive number, got {self._config.maxsize}"
            logger.error(msg)
            raise ConfigurationError(msg)

    @classmethod
    @abstractmethod
    def is_available(cls) -> bool:
        """
        Check if this cache engine is available.

        Returns:
            bool: True if the cache engine is available, False otherwise
        """

    def cleanup(self) -> None:
        """
        Clean up resources used by the cache engine.

        This method should be called when the cache is no longer needed to ensure
        proper resource cleanup. Implementations should override this method if they
        need to perform specific cleanup actions.
        """
        logger.debug(f"Cleaning up {self.__class__.__name__} resources")
        self._cache.clear()

    def _check_ttl(self, timestamp: float | None) -> bool:
        """
        Check if a cache entry has expired based on its timestamp.

        Args:
            timestamp: The timestamp when the entry was created, or None if no TTL

        Returns:
            bool: True if the entry is still valid, False if expired
        """
        if timestamp is None or self._config.ttl is None:
            return True

        return (time.time() - timestamp) < self._config.ttl

    def _make_key(self, func: Callable[P, R], args: Any, kwargs: Any) -> CacheKey:
        """
        Create a cache key for the given function and arguments.

        Args:
            func: The function being cached
            args: Positional arguments
            kwargs: Keyword arguments

        Returns:
            A cache key suitable for lookup
        """
        return create_cache_key(func, args, kwargs)

    @abstractmethod
    def cache(self, func: Callable[P, R]) -> Callable[P, R]:
        """
        Decorate a function to cache its results.

        Args:
            func: The function to cache

        Returns:
            A wrapped function that uses the cache
        """

    @abstractmethod
    def _get_cached_value(self, key: CacheKey) -> R | None:
        """
        Retrieve a value from the cache.

        Args:
            key: The cache key to look up

        Returns:
            The cached value if found, None otherwise
        """
        ...

    @abstractmethod
    def _set_cached_value(self, key: CacheKey, value: R) -> None:
        """
        Store a value in the cache.

        Args:
            key: The cache key to store under
            value: The value to cache
        """
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clear all cached values."""
        ...

    def get(self, key: str) -> R | None:
        """Get a value from the cache."""
        return self._get_cached_value(key)

    def set(self, key: str, value: R) -> None:
        """Set a value in the cache."""
        self._set_cached_value(key, value)

    @property
    def name(self) -> str:
        """Get the name of the cache engine."""
        return self.__class__.__name__


class CacheEngine(BaseCacheEngine[P, R]):
    """
    Concrete implementation of the cache engine protocol.

    This class provides a default implementation using a simple in-memory
    dictionary cache with the configured eviction policy.
    """

    def _get_cached_value(self, key: CacheKey) -> R | None:
        """
        Retrieve a value from the cache.

        Args:
            key: The cache key to look up

        Returns:
            The cached value if found and not expired, None otherwise
        """
        if key not in self._cache:
            return None

        value, expiry = self._cache[key]
        if expiry is not None and expiry <= 0:
            del self._cache[key]
            self._size -= 1
            return None

        return value

    def _set_cached_value(self, key: CacheKey, value: R) -> None:
        """
        Store a value in the cache.

        Args:
            key: The cache key to store under
            value: The value to cache
        """
        # Check maxsize
        if self._config.maxsize is not None and self._size >= self._config.maxsize:
            # Remove oldest item based on policy
            if self._config.policy == "lru":
                # Remove least recently used
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                self._size -= 1
            elif self._config.policy == "fifo":
                # Remove first item added
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                self._size -= 1
            # Other policies would be implemented here

        # Store with TTL if configured
        expiry = self._config.ttl
        self._cache[key] = (value, expiry)
        self._size += 1

    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()
        self._size = 0
        self._hits = 0
        self._misses = 0

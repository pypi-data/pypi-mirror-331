#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "loguru",
#   "redis",
# ]
# ///
# this_file: src/twat_cache/engines/redis.py

"""Redis-based cache engine."""

from __future__ import annotations

import pickle
import time
from functools import wraps
from typing import Any, cast
from collections.abc import Callable

from loguru import logger

from twat_cache.config import CacheConfig
from twat_cache.exceptions import (
    EngineNotAvailableError,
    CacheOperationError,
    ConfigurationError,
)
from twat_cache.type_defs import CacheKey, P, R
from .base import BaseCacheEngine, is_package_available


class RedisCacheEngine(BaseCacheEngine[P, R]):
    """
    Redis-based cache engine.

    This engine provides distributed caching using Redis, with support for:
    - TTL-based expiration
    - Compression
    - Serialization of complex objects
    - Distributed cache invalidation
    """

    @classmethod
    def is_available(cls) -> bool:
        """Check if Redis is available."""
        return is_package_available("redis")

    def __init__(self, config: CacheConfig) -> None:
        """Initialize the Redis engine.

        Args:
            config: Cache configuration settings.

        Raises:
            EngineNotAvailableError: If Redis is not available.
            ConfigurationError: If the configuration is invalid.
        """
        if not self.is_available():
            msg = "Redis is not available. Install with 'pip install redis'"
            raise EngineNotAvailableError(msg)

        super().__init__(config)

        # Import Redis here to avoid import errors if Redis is not installed
        import redis

        # Get Redis connection parameters from environment or use defaults
        host = config.get_redis_host() if hasattr(config, "get_redis_host") else "localhost"
        port = config.get_redis_port() if hasattr(config, "get_redis_port") else 6379
        db = config.get_redis_db() if hasattr(config, "get_redis_db") else 0
        password = config.get_redis_password() if hasattr(config, "get_redis_password") else None

        # Create Redis client
        try:
            self._redis = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=False,  # We need bytes for pickle
            )
            # Test connection
            self._redis.ping()
            logger.debug(f"Connected to Redis at {host}:{port} (db={db})")
        except redis.exceptions.ConnectionError as e:
            msg = f"Failed to connect to Redis at {host}:{port}: {e}"
            logger.error(msg)
            raise ConfigurationError(msg) from e

        # Set up namespace for keys
        self._namespace = config.folder_name or "twat_cache"

        # Set up serialization
        self._compress = config.compress

        # Statistics
        self._size_cache = None
        self._last_size_check = 0

    def validate_config(self) -> None:
        """Validate the Redis engine configuration.

        Raises:
            ConfigurationError: If the configuration is invalid.
        """
        super().validate_config()

        # Redis-specific validation
        if hasattr(self._config, "get_redis_port") and self._config.get_redis_port() is not None:
            port = self._config.get_redis_port()
            if not isinstance(port, int) or port <= 0 or port > 65535:
                msg = f"Invalid Redis port: {port}"
                raise ConfigurationError(msg)

    def cleanup(self) -> None:
        """Clean up Redis resources."""
        # Redis connections are automatically cleaned up
        # but we'll explicitly close it to be safe
        try:
            if hasattr(self, "_redis"):
                self._redis.close()
                logger.debug("Closed Redis connection")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")

    def _get_full_key(self, key: CacheKey) -> str:
        """Get the full Redis key with namespace.

        Args:
            key: Cache key.

        Returns:
            str: Full Redis key.
        """
        if isinstance(key, tuple):
            key_str = str(hash(key))
        else:
            key_str = str(key)

        return f"{self._namespace}:{key_str}"

    def _get_cached_value(self, key: CacheKey) -> R | None:
        """Get a cached value from Redis.

        Args:
            key: Cache key.

        Returns:
            Any: Cached value, or None if not found.
        """
        try:
            full_key = self._get_full_key(key)
            data = self._redis.get(full_key)

            if data is None:
                self._misses += 1
                return None

            # Deserialize the data
            try:
                if self._compress:
                    import zlib

                    data = zlib.decompress(data)

                value = pickle.loads(data)
                self._hits += 1
                self._last_access = time.time()
                return cast(R, value)
            except Exception as e:
                logger.error(f"Error deserializing cached value: {e}")
                self._misses += 1
                return None

        except Exception as e:
            logger.error(f"Error getting cached value from Redis: {e}")
            self._misses += 1
            return None

    def _set_cached_value(self, key: CacheKey, value: R) -> None:
        """Set a cached value in Redis.

        Args:
            key: Cache key.
            value: Value to cache.
        """
        try:
            full_key = self._get_full_key(key)

            # Serialize the value
            try:
                data = pickle.dumps(value)

                if self._compress:
                    import zlib

                    data = zlib.compress(data)
            except Exception as e:
                logger.error(f"Error serializing value: {e}")
                msg = f"Error serializing value: {e}"
                raise CacheOperationError(msg) from e

            # Set TTL if configured
            if self._config.ttl is not None:
                self._redis.setex(full_key, int(self._config.ttl), data)
            else:
                self._redis.set(full_key, data)

            self._last_update = time.time()
            self._size_cache = None  # Invalidate size cache

        except Exception as e:
            logger.error(f"Error setting cached value in Redis: {e}")
            msg = f"Error setting cached value in Redis: {e}"
            raise CacheOperationError(msg) from e

    def clear(self) -> None:
        """Clear all cached values in the namespace."""
        try:
            # Find all keys in our namespace
            pattern = f"{self._namespace}:*"
            keys = self._redis.keys(pattern)

            if keys:
                # Delete all keys in our namespace
                self._redis.delete(*keys)
                logger.debug(f"Cleared {len(keys)} keys from Redis namespace {self._namespace}")

            self._hits = 0
            self._misses = 0
            self._size_cache = None

        except Exception as e:
            logger.error(f"Error clearing Redis cache: {e}")
            msg = f"Error clearing Redis cache: {e}"
            raise CacheOperationError(msg) from e

    def cache(self, func: Callable[P, R]) -> Callable[P, R]:
        """Decorate a function to cache its results in Redis.

        Args:
            func: Function to cache.

        Returns:
            Callable: Decorated function.
        """

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # Create a cache key
            key = self._make_key(func, args, kwargs)

            # Try to get the cached value
            cached = self._get_cached_value(key)

            if cached is not None:
                return cached

            # Call the function and cache the result
            result = func(*args, **kwargs)
            self._set_cached_value(key, result)
            return result

        return wrapper

    @property
    def stats(self) -> dict[str, Any]:
        """Get Redis cache statistics.

        Returns:
            dict: Dictionary containing cache statistics.
        """
        base_stats = super().stats

        # Get current size (number of keys)
        current_time = time.time()
        if self._size_cache is None or current_time - self._last_size_check > 60:
            try:
                pattern = f"{self._namespace}:*"
                size = len(self._redis.keys(pattern))
                self._size_cache = size
                self._last_size_check = current_time
            except Exception as e:
                logger.error(f"Error getting Redis cache size: {e}")
                size = 0
        else:
            size = self._size_cache

        # Add Redis-specific stats
        redis_stats = {
            "size": size,
            "engine": "redis",
            "namespace": self._namespace,
            "compress": self._compress,
        }

        # Try to get Redis info
        try:
            info = self._redis.info()
            redis_stats.update(
                {
                    "redis_version": info.get("redis_version"),
                    "used_memory": info.get("used_memory"),
                    "used_memory_human": info.get("used_memory_human"),
                    "connected_clients": info.get("connected_clients"),
                }
            )
        except Exception as e:
            logger.debug(f"Error getting Redis info: {e}")

        return {**base_stats, **redis_stats}

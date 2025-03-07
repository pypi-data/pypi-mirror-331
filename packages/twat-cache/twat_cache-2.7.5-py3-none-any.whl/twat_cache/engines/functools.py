#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "loguru",
# ]
# ///
# this_file: src/twat_cache/engines/functools.py

"""
Functools-based cache engine implementation.

This module provides a basic cache engine implementation using Python's built-in
functools.lru_cache. It serves as a fallback when no other caching backends
are available.
"""

import functools
import time
from typing import Any
from collections.abc import Callable

from loguru import logger

from twat_cache.engines.base import BaseCacheEngine
from twat_cache.type_defs import CacheConfig, P, R, CacheKey


class FunctoolsCacheEngine(BaseCacheEngine[P, R]):
    """Cache engine implementation using functools.lru_cache."""

    @classmethod
    def is_available(cls) -> bool:
        """Check if functools is available."""
        return True  # Always available as it's in the standard library

    def __init__(self, config: CacheConfig) -> None:
        """Initialize the cache engine with the given configuration."""
        super().__init__(config)
        self._hits = 0
        self._misses = 0
        self._cache: dict[CacheKey, R] = {}
        self._maxsize = config.maxsize or None
        self._ttl = config.ttl
        self._last_access: dict[CacheKey, float] = {}

    def cache(self, func: Callable[P, R]) -> Callable[P, R]:
        """
        Decorate a function to cache its results.

        Args:
            func: The function to cache

        Returns:
            A wrapped function that caches its results
        """
        if self._maxsize is not None:
            wrapper = functools.lru_cache(maxsize=self._maxsize)(func)
        else:
            wrapper = functools.cache(func)

        def cached_func(*args: P.args, **kwargs: P.kwargs) -> R:
            key = self._make_key(*args, **kwargs)

            # Check TTL
            if self._ttl is not None:
                now = time.time()
                if key in self._last_access:
                    if now - self._last_access[key] > self._ttl:
                        self.clear()
                        self._misses += 1
                        result = func(*args, **kwargs)
                        self._cache[key] = result
                        self._last_access[key] = now
                        return result

            # Try to get from cache
            try:
                result = wrapper(*args, **kwargs)
                self._hits += 1
                self._cache[key] = result
                self._last_access[key] = time.time()
                return result
            except Exception as e:
                self._misses += 1
                logger.warning(f"Cache miss for {key}: {e}")
                result = func(*args, **kwargs)
                self._cache[key] = result
                self._last_access[key] = time.time()
                return result

        return cached_func

    def clear(self) -> None:
        """Clear all cached values."""
        if hasattr(self, "_cache"):
            self._cache.clear()
            self._last_access.clear()
            self._hits = 0
            self._misses = 0

    def validate_config(self) -> None:
        """
        Validate the engine configuration.

        Raises:
            ValueError: If the configuration is invalid
        """
        if self._config.maxsize is not None and self._config.maxsize <= 0:
            msg = "maxsize must be positive"
            raise ValueError(msg)

        if self._config.ttl is not None and self._config.ttl < 0:
            msg = "ttl must be non-negative"
            raise ValueError(msg)

    @property
    def stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            A dictionary containing cache statistics:
            - hits: Number of cache hits
            - misses: Number of cache misses
            - size: Current number of items in cache
            - maxsize: Maximum number of items allowed
        """
        return {
            "hits": self._hits,
            "misses": self._misses,
            "size": len(self._cache),
            "maxsize": self._maxsize,
            "backend": "functools",
            "policy": "lru" if self._maxsize else None,
            "ttl": self._ttl,
        }

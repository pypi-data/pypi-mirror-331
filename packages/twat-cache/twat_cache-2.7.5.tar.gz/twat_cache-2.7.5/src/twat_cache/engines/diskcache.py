#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "loguru",
#   "diskcache",
#   "types-diskcache",
# ]
# ///
# this_file: src/twat_cache/engines/diskcache.py

"""Disk-based cache engine using diskcache."""

from __future__ import annotations

import time
from functools import wraps
from typing import Any, cast
from collections.abc import Callable

# Skipping analyzing "diskcache": module is installed, but missing library stubs or py.typed marker
from diskcache import Cache  # type: ignore
from loguru import logger

from twat_cache.config import CacheConfig
from twat_cache.exceptions import (
    EngineNotAvailableError,
    CacheOperationError,
    ResourceError,
)
from twat_cache.type_defs import P, R
from .base import BaseCacheEngine
from .common import ensure_dir_exists


class DiskCacheEngine(BaseCacheEngine[P, R]):
    """
    Disk-based cache engine using diskcache.

    This engine provides persistent caching using SQLite and the filesystem,
    with support for TTL, compression, and secure file permissions.
    """

    @classmethod
    def is_available(cls) -> bool:
        """Check if diskcache is available."""
        try:
            import diskcache

            return True
        except ImportError:
            return False

    def __init__(self, config: CacheConfig) -> None:
        """Initialize the disk cache engine."""
        super().__init__(config)

        if not self._cache_path:
            logger.error("Cache path is required for disk cache")
            msg = "diskcache"
            raise EngineNotAvailableError(
                msg, "Cache path is required but not provided"
            )

        if not self.is_available():
            logger.error("diskcache is not available")
            msg = "diskcache"
            raise EngineNotAvailableError(
                msg,
                "Package is not installed. Install with 'pip install diskcache'",
            )

        try:
            # Ensure cache directory exists with proper permissions
            ensure_dir_exists(
                self._cache_path, mode=0o700 if self._config.secure else 0o755
            )

            # Initialize DiskCache with the configuration
            self._disk_cache = Cache(
                directory=str(self._cache_path),
                size_limit=self._config.maxsize,
                disk_min_file_size=0,  # Cache everything to disk
                statistics=True,
                tag_index=True,
                disk_pickle_protocol=4,
            )

            logger.debug(f"Initialized DiskCache at {self._cache_path}")
        except Exception as e:
            logger.error(f"Failed to initialize DiskCache: {e}")
            msg = f"Failed to initialize DiskCache: {e!s}"
            raise ResourceError(msg) from e

    def cleanup(self) -> None:
        """Clean up resources used by the cache engine."""
        try:
            if hasattr(self, "_disk_cache") and self._disk_cache is not None:
                self._disk_cache.close()
                logger.debug(f"Closed DiskCache at {self._cache_path}")
        except Exception as e:
            logger.error(f"Error closing DiskCache: {e}")
        finally:
            super().cleanup()

    def cache(self, func: Callable[P, R]) -> Callable[P, R]:
        """
        Decorate a function to cache its results using DiskCache.

        Args:
            func: The function to cache

        Returns:
            A wrapped function that uses disk cache
        """

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # Create a cache key
            key = self._make_key(func, args, kwargs)

            try:
                # Check if value is in cache with expire_time=True to get expiry info
                cache_result = self._disk_cache.get(key, default=None, expire_time=True)

                if cache_result is not None:
                    # The result structure is complicated, extract carefully
                    if isinstance(cache_result, tuple) and len(cache_result) >= 2:
                        cached_value, expire_time = cache_result[0], cache_result[1]

                        # Check if entry has expired
                        if expire_time is None or (
                            isinstance(expire_time, int | float)
                            and time.time() < expire_time
                        ):
                            self._hits += 1
                            logger.trace(f"Cache hit for {func.__name__}")
                            return cast(R, cached_value)
                        else:
                            # Expired entry, remove it
                            self._disk_cache.delete(key)

                # Cache miss - compute value
                self._misses += 1
                logger.trace(f"Cache miss for {func.__name__}")

                result = func(*args, **kwargs)

                # Calculate expire time if TTL is set
                expire_time = None
                if self._config.ttl is not None:
                    expire_time = time.time() + self._config.ttl

                # Store in cache
                self._disk_cache.set(
                    key=key,
                    value=(result, expire_time),
                    expire=self._config.ttl,
                    tag=func.__module__ + "." + func.__name__,
                    retry=True,
                )

                # Update cache size stat (safely)
                try:
                    self._size = self._disk_cache.volume()
                except Exception:
                    # Fallback if volume() not available
                    self._size += 1

                return result

            except Exception as e:
                logger.error(f"Error in DiskCache: {e}")
                # Fall back to calling the function directly
                return func(*args, **kwargs)

        return wrapper

    def clear(self) -> None:
        """Clear all entries from the cache."""
        try:
            if hasattr(self, "_disk_cache") and self._disk_cache is not None:
                self._disk_cache.clear()
                self._hits = 0
                self._misses = 0
                self._size = 0
                logger.debug(f"Cleared DiskCache at {self._cache_path}")
        except Exception as e:
            logger.error(f"Error clearing DiskCache: {e}")
            msg = f"Failed to clear DiskCache: {e!s}"
            raise CacheOperationError(msg) from e

    @property
    def stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        base_stats = super().stats

        try:
            if hasattr(self, "_disk_cache") and self._disk_cache is not None:
                # Get statistics dictionary safely
                disk_stats_dict = self._disk_cache.stats(enable=True)

                # Safely update stats dictionary
                if isinstance(disk_stats_dict, dict):
                    base_stats["disk_hits"] = disk_stats_dict.get("hits", 0)
                    base_stats["disk_misses"] = disk_stats_dict.get("misses", 0)

                # Get size and volume safely
                try:
                    base_stats["disk_size"] = self._disk_cache.volume()
                except Exception:
                    base_stats["disk_size"] = 0

        except Exception as e:
            logger.error(f"Error getting DiskCache stats: {e}")

        return base_stats

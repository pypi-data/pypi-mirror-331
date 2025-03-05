#!/usr/bin/env python3
"""
Flexible caching utilities for Python functions.

This module provides a unified interface for caching function results using various
backends (memory, disk, SQL). It automatically handles cache directory management
and offers a simple decorator interface.

Example:
    from twat_cache import ucache

    @ucache()
    def expensive_computation(x):
        return x * x

    # Results will be cached automatically
    result = expensive_computation(42)
"""

from __future__ import annotations

import inspect
import uuid
from collections.abc import Callable
from functools import cache
from pathlib import Path
from typing import Any, TypeVar

from twat_cache.cache import cache as twat_cache
from twat_cache.config import CacheConfig

T = TypeVar("T")


@cache
def get_cache_path(folder_name: str | None = None) -> Path:
    """
    Get or create a cache directory path.

    Args:
        folder_name: Optional name for the cache folder. If None, generates a UUID
            based on the caller's file path.

    Returns:
        Path: The resolved cache directory path.
    """

    def generate_uuid() -> str:
        """Generate a UUID based on the file of the caller."""
        caller_frame = inspect.stack()[2]
        caller_file = caller_frame.filename
        caller_path = Path(caller_file).resolve()
        return str(uuid.uuid5(uuid.NAMESPACE_URL, str(caller_path)))

    if folder_name is None:
        folder_name = generate_uuid()

    cache_dir = (
        Path.home() / ".cache" / "twat_cache" / str(folder_name)
    )  # TODO use twat.paths
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


# Initialize optional caching backends
try:
    from diskcache import Cache

    DISK_CACHE: Any | None = Cache(get_cache_path("twat_cache"))
except ImportError:
    DISK_CACHE = None

try:
    from joblib import Memory

    JOBLIB_MEMORY: Any | None = Memory(get_cache_path("twat_cache"), verbose=0)
except ImportError:
    JOBLIB_MEMORY = None


def ucache(
    folder_name: str | None = None,
    *,
    use_sql: bool = False,
    maxsize: int | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for caching function results with user-specific storage.

    This decorator provides a way to cache function results in a user-specific
    location, with optional SQL-based persistent storage.

    Args:
        folder_name: Optional name for the cache folder. If not provided,
            a default location will be used.
        use_sql: Whether to use SQL-based persistent storage instead of
            in-memory caching. Defaults to False.
        maxsize: Maximum size of the cache. If None, the cache size is
            unlimited. Defaults to None.

    Returns:
        A decorator function that will cache the results of the decorated
        function.

    Example:
        >>> @ucache(folder_name="my_cache", use_sql=True)
        ... def expensive_function(x: int) -> int:
        ...     return x * x
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        """Create a caching wrapper for the function."""
        config = CacheConfig(
            maxsize=maxsize,
            folder_name=folder_name,
            use_sql=use_sql,
        )
        return twat_cache(config)(func)

    return decorator

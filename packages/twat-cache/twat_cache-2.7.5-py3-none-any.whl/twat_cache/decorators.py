#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "loguru",
#   "functools",
#   "diskcache",
#   "joblib",
#   "types-diskcache",
#   "pydantic",
#   "aiocache",
#   "cachetools",
#   "cachebox",
#   "klepto",
#   "types-cachetools",
# ]
# ///
# this_file: src/twat_cache/decorators.py

"""
Core caching decorators.

This module provides five main decorators:
- mcache: Memory-based caching using fastest available backend (with fallback to functools)
- bcache: Basic disk caching using diskcache (with fallback to memory)
- fcache: Fast file-based caching using joblib (with fallback to memory)
- acache: Async-capable caching using aiocache (with fallback to async wrapper)
- ucache: Universal caching that automatically selects best available backend

These decorators provide a simple interface for caching function results with various
backends, automatically handling fallbacks if preferred backends are not available.
"""

import asyncio
import functools
import importlib.util
import json
from pathlib import Path
from typing import (
    Any,
    Protocol,
    cast,
)
from collections.abc import Awaitable, Callable

# Import the logger from our logging module
from .logging import logger

from .config import CacheConfig, create_cache_config, EvictionPolicy
from .engines.base import BaseCacheEngine
from .type_defs import P, R, AsyncR


class CacheDecorator(Protocol[P, R]):
    """
    Protocol for cache decorators.

    This protocol defines the interface for cache decorators that can be applied
    to synchronous functions. Cache decorators wrap functions to store and retrieve
    results based on input parameters.
    """

    def __call__(self, func: Callable[P, R]) -> Callable[P, R]: ...


class AsyncCacheDecorator(Protocol[P, AsyncR]):
    """
    Protocol for async cache decorators.

    This protocol defines the interface for cache decorators that can be applied
    to asynchronous functions. Async cache decorators wrap coroutine functions to
    store and retrieve results based on input parameters.
    """

    def __call__(
        self, func: Callable[P, AsyncR] | Callable[P, Awaitable[AsyncR]]
    ) -> Callable[P, Awaitable[AsyncR]]: ...


# Check optional backend availability
HAS_AIOCACHE = bool(importlib.util.find_spec("aiocache"))
HAS_CACHEBOX = bool(importlib.util.find_spec("cachebox"))
HAS_CACHETOOLS = bool(importlib.util.find_spec("cachetools"))
HAS_DISKCACHE = bool(importlib.util.find_spec("diskcache"))
HAS_JOBLIB = bool(importlib.util.find_spec("joblib"))
HAS_KLEPTO = bool(importlib.util.find_spec("klepto"))


def get_cache_dir(folder_name: str | None = None) -> Path:
    """
    Get or create cache directory.

    Creates a cache directory for storing cached data. The directory is created
    under the user's home directory in `.cache/twat_cache/[folder_name]`.
    If the directory already exists, it is returned as is.

    Args:
        folder_name: Optional name for the cache folder. If None, 'default' is used.
            Must contain only alphanumeric characters, dash, underscore, and dot.

    Returns:
        Path: Path object pointing to the cache directory.

    Raises:
        ValueError: If folder_name contains invalid characters.
        OSError: If directory creation fails due to permission issues or disk errors.

    Example:
        >>> cache_dir = get_cache_dir("my_app")
        >>> print(cache_dir)
        /home/user/.cache/twat_cache/my_app
    """
    if folder_name and not all(c.isalnum() or c in "-_." for c in folder_name):
        msg = f"Invalid folder name '{folder_name}'. Use only alphanumeric chars, dash, underscore and dot"
        raise ValueError(msg)

    base_dir = Path.home() / ".cache" / "twat_cache"
    cache_dir = base_dir / (folder_name or "default")

    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        msg = f"Failed to create cache directory {cache_dir}: {e}"
        raise OSError(msg) from e

    return cache_dir


def make_key(serializer: Callable[[Any], str] | None = None, *args: Any, **kwargs: Any) -> str:
    """
    Create a cache key from function arguments.

    Generates a unique string key based on the provided arguments. This key is used
    to identify cached values. The function handles serialization of arguments to
    ensure consistent key generation.

    Args:
        serializer: Optional function to serialize non-JSON-serializable objects.
            If None, a default serializer is used that converts objects to strings.
        *args: Positional arguments to include in the key.
        **kwargs: Keyword arguments to include in the key.

    Returns:
        str: A string key that uniquely identifies the arguments.

    Example:
        >>> make_key(None, 1, 2, name="test")
        '[[1, 2], {"name": "test"}]'

        >>> # With custom serializer
        >>> def my_serializer(obj):
        ...     if isinstance(obj, complex):
        ...         return [obj.real, obj.imag]
        ...     return str(obj)
        >>> make_key(my_serializer, complex(1, 2), name="test")
        '[[[1.0, 2.0]], {"name": "test"}]'
    """

    def default_serializer(obj: Any) -> Any:
        if isinstance(obj, str | int | float | bool | type(None)):
            return obj
        return str(obj)

    ser = serializer or default_serializer

    # Convert args and kwargs to stable forms
    converted_args = tuple(ser(arg) for arg in args)
    converted_kwargs = {k: ser(v) for k, v in sorted(kwargs.items())}

    # Create a stable string representation
    return json.dumps((converted_args, converted_kwargs), sort_keys=True)


def mcache(
    maxsize: int | None = None,
    ttl: float | None = None,
    policy: str = "lru",
    *,  # Force remaining arguments to be keyword-only
    secure: bool = True,
) -> CacheDecorator[P, R]:
    """
    Memory-based caching decorator.

    Creates a decorator that caches results in memory using the fastest available backend,
    with fallback to functools.lru_cache if no other backends are available.

    Args:
        maxsize: Maximum size of the cache. If None, the cache has no size limit.
        ttl: Time-to-live in seconds. If None, cached values never expire.
        policy: Cache eviction policy. Options: "lru", "fifo", "lifo", "mru", "lfu".
        secure: Whether to use secure key generation (slower but handles more types).

    Returns:
        A decorator function that can be applied to functions to cache their results.

    Examples:
        >>> @mcache(maxsize=100, ttl=60)
        ... def expensive_function(x, y):
        ...     # Some expensive computation
        ...     return x + y
    """
    logger.debug(f"Creating memory cache with maxsize={maxsize}, ttl={ttl}, policy={policy}")

    config = create_cache_config(
        folder_name=None,
        maxsize=maxsize,
        ttl=ttl,
        policy=policy,
        secure=secure,
        cache_type="memory",
    )

    if HAS_CACHEBOX:
        from .engines import cachebox

        logger.debug("Using CacheBox engine for memory caching")
        engine: BaseCacheEngine[P, R] = cachebox.CacheBoxEngine(config)  # type: ignore[abstract]
        return cast(CacheDecorator[P, R], engine.cache)
    elif HAS_CACHETOOLS:
        from .engines import cachetools

        logger.debug("Using CacheTools engine for memory caching")
        engine = cachetools.CacheToolsEngine(config)  # type: ignore[abstract]
        return cast(CacheDecorator[P, R], engine.cache)
    else:
        from .engines import functools_engine

        logger.debug("Using functools engine for memory caching (fallback)")
        engine = functools_engine.FunctoolsEngine(config)  # type: ignore[abstract]
        return cast(CacheDecorator[P, R], engine.cache)


def bcache(
    folder_name: str | None = None,
    maxsize: int | None = None,
    ttl: float | None = None,
    policy: str = "lru",
    *,  # Force remaining arguments to be keyword-only
    use_sql: bool = True,
    secure: bool = True,
) -> CacheDecorator[P, R]:
    """
    Basic disk caching decorator.

    Creates a decorator that caches results on disk using diskcache, with fallback to
    memory caching if diskcache is not available.

    Args:
        folder_name: Name of the folder to store cache files. If None, a default is used.
        maxsize: Maximum size of the cache. If None, the cache has no size limit.
        ttl: Time-to-live in seconds. If None, cached values never expire.
        policy: Cache eviction policy. Options: "lru", "fifo", "lifo", "mru", "lfu".
        use_sql: Whether to use SQL-based disk cache (if available).
        secure: Whether to use secure key generation (slower but handles more types).

    Returns:
        A decorator function that can be applied to functions to cache their results.

    Examples:
        >>> @bcache(folder_name="my_cache", ttl=3600)
        ... def expensive_function(x, y):
        ...     # Some expensive computation
        ...     return x + y
    """
    logger.debug(f"Creating disk cache with folder={folder_name}, maxsize={maxsize}, ttl={ttl}, use_sql={use_sql}")

    config = create_cache_config(
        folder_name=folder_name,
        maxsize=maxsize,
        ttl=ttl,
        policy=policy,
        secure=secure,
        cache_type="disk",
    )

    if HAS_DISKCACHE:
        from .engines import diskcache

        logger.debug("Using DiskCache engine for disk caching")
        engine: BaseCacheEngine[P, R] = diskcache.DiskCacheEngine(config)  # type: ignore[abstract]
        return cast(CacheDecorator[P, R], engine.cache)
    elif HAS_KLEPTO and use_sql:
        from .engines import klepto

        logger.debug("Using Klepto engine for disk caching (SQL)")
        engine = klepto.KleptoEngine(config)
        return cast(CacheDecorator[P, R], engine.cache)
    else:
        logger.warning("No disk cache backends available, falling back to memory cache")
        return mcache(maxsize=maxsize, ttl=ttl, policy=policy, secure=secure)


def fcache(
    folder_name: str | None = None,
    maxsize: int | None = None,
    ttl: float | None = None,
    *,  # Force remaining arguments to be keyword-only
    compress: bool = False,
    secure: bool = True,
) -> CacheDecorator[P, R]:
    """
    Fast file-based caching decorator.

    Creates a decorator that caches results in files using joblib, with fallback to
    memory caching if joblib is not available.

    Args:
        folder_name: Name of the folder to store cache files. If None, a default is used.
        maxsize: Maximum size of the cache. If None, the cache has no size limit.
        ttl: Time-to-live in seconds. If None, cached values never expire.
        compress: Whether to compress cached values.
        secure: Whether to use secure key generation (slower but handles more types).

    Returns:
        A decorator function that can be applied to functions to cache their results.

    Examples:
        >>> @fcache(folder_name="my_cache", compress=True)
        ... def expensive_function(x, y):
        ...     # Some expensive computation
        ...     return x + y
    """
    logger.debug(f"Creating file cache with folder={folder_name}, maxsize={maxsize}, ttl={ttl}, compress={compress}")

    config = create_cache_config(
        folder_name=folder_name,
        maxsize=maxsize,
        ttl=ttl,
        compress=compress,
        secure=secure,
        cache_type="file",
    )

    if HAS_JOBLIB:
        from .engines.joblib import JoblibEngine

        logger.debug("Using Joblib engine for file caching")
        engine: BaseCacheEngine[P, R] = JoblibEngine(config)
        return cast(CacheDecorator[P, R], engine.cache)
    elif HAS_KLEPTO:
        from .engines.klepto import KleptoEngine

        logger.debug("Using Klepto engine for file caching (fallback)")
        engine = KleptoEngine(config)
        return cast(CacheDecorator[P, R], engine.cache)
    else:
        logger.warning("No file cache backends available, falling back to memory cache")
        return mcache(maxsize=maxsize, ttl=ttl)


def acache(
    maxsize: int | None = None,
    ttl: float | None = None,
    policy: EvictionPolicy = "lru",
) -> (
    Callable[[Callable[P, Awaitable[AsyncR]]], Callable[P, Awaitable[AsyncR]]]
    | Callable[[Callable[P, AsyncR]], Callable[P, Awaitable[AsyncR]]]
):
    """
    Async-capable caching decorator.

    Creates a decorator that caches results of asynchronous functions. This decorator
    works with both coroutine functions and regular functions that return awaitable objects.
    It automatically handles the asynchronous nature of the cached functions.

    Args:
        maxsize: Maximum size of the cache. If None, the cache has no size limit.
        ttl: Time-to-live in seconds. If None, cached values never expire.
        policy: Cache eviction policy. Options: "lru", "fifo", "lifo", "mru", "lfu".

    Returns:
        A decorator function that can be applied to async functions to cache their results.

    Examples:
        >>> @acache(maxsize=100, ttl=60)
        ... async def expensive_async_function(x, y):
        ...     # Some expensive async computation
        ...     return x + y
    """
    logger.debug(f"Creating async cache with maxsize={maxsize}, ttl={ttl}, policy={policy}")

    config = create_cache_config(
        folder_name=None,
        maxsize=maxsize,
        ttl=ttl,
        policy=policy,
        cache_type="memory",
    )

    if HAS_AIOCACHE:
        from .engines import aiocache

        logger.debug("Using AioCache engine for async caching")

        def decorator(
            func: Callable[P, AsyncR] | Callable[P, Awaitable[AsyncR]],
        ) -> Callable[P, Awaitable[AsyncR]]:
            """Decorator that wraps a function with async caching."""
            # Create the engine instance inside the decorator where it's actually used
            engine: Any = aiocache.AioCacheEngine(config)  # type: ignore[abstract]
            cache_func = engine.cache(func)

            @functools.wraps(func)
            async def wrapper(*args: P.args, **kwargs: P.kwargs) -> AsyncR:
                return await cache_func(*args, **kwargs)

            return wrapper

        return decorator
    else:
        logger.warning("AioCache not available, using memory cache with async wrapper")
        # Fallback to a memory cache with async wrapper
        mem_cache = mcache(maxsize=maxsize, ttl=ttl, policy=str(policy))

        def decorator(
            func: Callable[P, AsyncR] | Callable[P, Awaitable[AsyncR]],
        ) -> Callable[P, Awaitable[AsyncR]]:
            cached_func = mem_cache(func)  # type: ignore

            @functools.wraps(func)
            async def wrapper(*args: P.args, **kwargs: P.kwargs) -> AsyncR:
                if asyncio.iscoroutinefunction(func):
                    # If it's already a coroutine function, we need to await the result
                    return await cached_func(*args, **kwargs)  # type: ignore
                else:
                    # If it's a regular function that returns an awaitable
                    return await cached_func(*args, **kwargs)

            return wrapper

        return decorator


def _get_available_backends() -> dict[str, bool]:
    """
    Get a dictionary of available cache backends.

    Checks which cache backends are available in the current environment
    by checking if the required packages are installed.

    Returns:
        dict[str, bool]: Dictionary mapping backend names to availability status.

    Example:
        >>> backends = _get_available_backends()
        >>> print(backends)
        {'aiocache': True, 'cachebox': False, 'cachetools': True, 'diskcache': True, 'joblib': True}
    """
    return {
        "aiocache": HAS_AIOCACHE,
        "cachebox": HAS_CACHEBOX,
        "cachetools": HAS_CACHETOOLS,
        "diskcache": HAS_DISKCACHE,
        "joblib": HAS_JOBLIB,
        "klepto": HAS_KLEPTO,
    }


def _select_best_backend(
    preferred: str | None = None,
    *,  # Force remaining arguments to be keyword-only
    is_async: bool = False,
    needs_disk: bool = False,
) -> str:
    """
    Select the best available backend based on requirements.

    Determines the most suitable cache backend based on the specified preferences
    and requirements. It considers whether async support is needed and whether
    disk storage is required.

    Args:
        preferred: Name of the preferred backend. If available, this backend will be used.
            If not available, a suitable alternative will be selected.
        is_async: Whether async support is required. If True, only backends with
            async support will be considered.
        needs_disk: Whether disk storage is required. If True, only backends with
            disk storage capabilities will be considered.

    Returns:
        str: Name of the selected backend.

    Raises:
        ImportError: If no suitable backend is available for the specified requirements.

    Example:
        >>> # Select best backend with disk storage
        >>> backend = _select_best_backend(needs_disk=True)
        >>> print(backend)
        'diskcache'

        >>> # Select best async backend
        >>> backend = _select_best_backend(is_async=True)
        >>> print(backend)
        'aiocache'
    """
    backends = _get_available_backends()

    # If preferred backend is available and meets requirements, use it
    if preferred and backends.get(preferred):
        if is_async and preferred != "aiocache":
            # Only aiocache supports async natively
            pass
        elif needs_disk and preferred not in ("diskcache", "klepto", "joblib"):
            # Only these backends support disk storage
            pass
        else:
            return preferred

    # Select based on requirements
    if is_async:
        if backends["aiocache"]:
            return "aiocache"
        # No good async fallback, will need to wrap
        if needs_disk:
            if backends["diskcache"]:
                return "diskcache"
            elif backends["klepto"]:
                return "klepto"
            elif backends["joblib"]:
                return "joblib"
        elif backends["cachebox"]:
            return "cachebox"
        elif backends["cachetools"]:
            return "cachetools"
    elif needs_disk:
        if backends["diskcache"]:
            return "diskcache"
        elif backends["klepto"]:
            return "klepto"
        elif backends["joblib"]:
            return "joblib"
    elif backends["cachebox"]:
        return "cachebox"
    elif backends["cachetools"]:
        return "cachetools"

    # Fallback to functools (always available)
    return "functools"


def _create_engine(config: CacheConfig, func: Callable[P, R]) -> BaseCacheEngine[P, R]:
    """
    Create a cache engine based on configuration.

    Instantiates the appropriate cache engine based on the provided configuration
    and the function to be cached. This is an internal function used by the ucache
    decorator to create the most suitable engine.

    Args:
        config: Configuration for the cache engine, including parameters like
            maxsize, ttl, policy, and cache type.
        func: The function that will be cached. Used to determine if the function
            is asynchronous.

    Returns:
        BaseCacheEngine: An instance of the appropriate cache engine.

    Raises:
        ImportError: If the required backend is not available.
        ValueError: If the configuration is invalid.

    Example:
        >>> def example_func(x, y):
        ...     return x + y
        >>>
        >>> config = create_cache_config(maxsize=100, ttl=60)
        >>> engine = _create_engine(config, example_func)
        >>> print(type(engine).__name__)
        'CacheToolsEngine'
    """
    # Check if function is async
    is_async = asyncio.iscoroutinefunction(func)
    needs_disk = config.cache_type in ("disk", "file")

    # Select backend
    backend = _select_best_backend(config.preferred_engine, is_async=is_async, needs_disk=needs_disk)

    # Create engine based on selected backend - import modules instead of directly
    # instantiating classes to avoid linter errors about abstract methods
    if backend == "aiocache" and HAS_AIOCACHE:
        from .engines import aiocache

        return aiocache.AioCacheEngine(config)  # type: ignore[abstract]
    elif backend == "cachebox" and HAS_CACHEBOX:
        from .engines import cachebox

        return cachebox.CacheBoxEngine(config)  # type: ignore[abstract]
    elif backend == "cachetools" and HAS_CACHETOOLS:
        from .engines import cachetools

        return cachetools.CacheToolsEngine(config)  # type: ignore[abstract]
    elif backend == "diskcache" and HAS_DISKCACHE:
        from .engines import diskcache

        return diskcache.DiskCacheEngine(config)  # type: ignore[abstract]
    elif backend == "joblib" and HAS_JOBLIB:
        from .engines import joblib

        return joblib.JoblibEngine(config)  # type: ignore[abstract]
    elif backend == "klepto" and HAS_KLEPTO:
        from .engines import klepto

        return klepto.KleptoEngine(config)  # type: ignore[abstract]
    else:
        # Always fallback to functools which is guaranteed to be available
        from .engines import functools_engine

        return functools_engine.FunctoolsCacheEngine(config)  # type: ignore[abstract]


def ucache(
    folder_name: str | None = None,
    maxsize: int | None = None,
    ttl: float | None = None,
    policy: str = "lru",
    preferred_engine: str | None = None,
    *,  # Force remaining arguments to be keyword-only
    use_sql: bool = False,
    compress: bool = False,
    secure: bool = True,
) -> CacheDecorator[P, R]:
    """
    Universal caching decorator.

    Creates a decorator that automatically selects the best available caching backend
    based on the function's characteristics and available backends.

    Args:
        folder_name: Name of the folder to store cache files. If None, a default is used.
        maxsize: Maximum size of the cache. If None, the cache has no size limit.
        ttl: Time-to-live in seconds. If None, cached values never expire.
        policy: Cache eviction policy. Options: "lru", "fifo", "lifo", "mru", "lfu".
        preferred_engine: Preferred caching engine. If not available, falls back to best available.
        use_sql: Whether to use SQL-based disk cache (if available).
        compress: Whether to compress cached values.
        secure: Whether to use secure key generation (slower but handles more types).

    Returns:
        A decorator function that can be applied to functions to cache their results.

    Examples:
        >>> @ucache(preferred_engine="joblib", compress=True)
        ... def expensive_function(x, y):
        ...     # Some expensive computation
        ...     return x + y
    """
    logger.debug(f"Creating universal cache with preferred_engine={preferred_engine}")

    config = create_cache_config(
        folder_name=folder_name,
        maxsize=maxsize,
        ttl=ttl,
        policy=policy,
        use_sql=use_sql,
        compress=compress,
        secure=secure,
        cache_type="auto",
    )

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        """Decorator that wraps a function with the best available caching backend."""
        # Determine if the function is async
        is_async = asyncio.iscoroutinefunction(func)

        # Determine if we need disk caching based on the function's characteristics
        needs_disk = False

        # Select the best backend
        backend = preferred_engine or _select_best_backend(is_async=is_async, needs_disk=needs_disk)

        logger.debug(f"Selected {backend} backend for {func.__name__}")

        # Create the appropriate engine
        engine = _create_engine(config, func)

        # Apply the cache decorator
        cached_func = engine.cache(func)

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                return cached_func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Cache error in {func.__name__}: {e}. Executing without cache.")
                return func(*args, **kwargs)

        return wrapper

    return decorator

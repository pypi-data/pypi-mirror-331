#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "loguru",
#   "pydantic",
# ]
# ///
# this_file: src/twat_cache/type_defs.py

"""
Core type definitions for twat-cache.

This module defines the fundamental types and type variables used throughout
the caching system, ensuring type safety and providing clear interfaces.
"""

from abc import ABC, abstractmethod
from typing import (
    Any,
    Generic,
    Protocol,
    TypeVar,
    Literal,
    runtime_checkable,
    ParamSpec,
)
from collections.abc import Callable, Awaitable
from pathlib import Path

# Type variables for generic cache types
T = TypeVar("T")
P = ParamSpec("P")
R = TypeVar("R")
F = TypeVar("F", bound=Callable[..., Any])
AsyncR = TypeVar("AsyncR")

# Cache key and value types
CacheKey = str | tuple[Any, ...]
CacheValue = Any  # Consider constraining this in future versions


# Protocol for cache decorators
class CacheDecorator(Protocol[P, R]):
    """Protocol for cache decorators."""

    def __call__(self, func: Callable[P, R]) -> Callable[P, R]: ...


# Protocol for async cache decorators
class AsyncCacheDecorator(Protocol[P, AsyncR]):
    """Protocol for async cache decorators."""

    def __call__(
        self,
        func: Callable[P, Awaitable[AsyncR]] | Callable[P, AsyncR],
    ) -> Callable[P, Awaitable[AsyncR]]: ...


# Type aliases for decorator functions
SyncDecorator = Callable[[Callable[P, R]], Callable[P, R]]
AsyncDecorator = Callable[
    [Callable[P, AsyncR] | Callable[P, Awaitable[AsyncR]]],
    Callable[P, Awaitable[AsyncR]],
]


@runtime_checkable
class CacheConfig(Protocol):
    """Protocol defining the required configuration interface for cache engines."""

    maxsize: int | None
    folder_name: str | None
    use_sql: bool
    preferred_engine: str | None
    cache_type: str | None

    def get_maxsize(self) -> int | None:
        """Get the maxsize value."""
        ...

    def get_folder_name(self) -> str | None:
        """Get the folder name."""
        ...

    def get_use_sql(self) -> bool:
        """Get the use_sql value."""
        ...

    def get_preferred_engine(self) -> str | None:
        """Get the preferred engine."""
        ...

    def get_cache_type(self) -> str | None:
        """Get the cache type."""
        ...

    def validate_config(self) -> None:
        """Validate the configuration."""
        ...

    def model_dump(self) -> dict[str, Any]:
        """Convert the model to a dictionary."""
        ...


class CacheStats(ABC):
    """Abstract base class defining the required statistics interface for cache engines."""

    @property
    @abstractmethod
    def hits(self) -> int:
        """Number of cache hits."""
        ...

    @property
    @abstractmethod
    def misses(self) -> int:
        """Number of cache misses."""
        ...

    @property
    @abstractmethod
    def size(self) -> int:
        """Current number of items in the cache."""
        ...

    @property
    @abstractmethod
    def maxsize(self) -> int | None:
        """Maximum number of items allowed in the cache."""
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clear all statistics."""
        ...


class CacheEngine(ABC, Generic[P, R]):
    """Abstract base class defining the required interface for cache engines."""

    def __init__(self, config: CacheConfig) -> None:
        """Initialize the cache engine with the given configuration."""
        self._config = config
        self.validate_config()

    @abstractmethod
    def cache(self, func: Callable[P, R]) -> Callable[P, R]:
        """
        Decorate a function to cache its results.

        Args:
            func: The function to cache

        Returns:
            A wrapped function that caches its results
        """
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clear all cached values."""
        ...

    @abstractmethod
    def validate_config(self) -> None:
        """
        Validate the engine configuration.

        Raises:
            ValueError: If the configuration is invalid
        """
        ...

    @property
    @abstractmethod
    def stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            A dictionary containing cache statistics:
            - hits: Number of cache hits
            - misses: Number of cache misses
            - size: Current number of items in cache
            - maxsize: Maximum number of items allowed
            - current_size: Current size of cache in bytes (if available)
            - memory_usage: Memory usage in bytes (if available)
        """
        ...


# Cache backend types
BackendType = Literal[
    "cachebox",  # Rust-based
    "cachetools",  # Flexible in-memory
    "aiocache",  # Async support with Redis
    "klepto",  # Scientific computing
    "diskcache",  # SQL-based disk cache
    "joblib",  # Array caching
    "memory",  # Always available
]

# Cache path types
CachePath = str | Path
CachePathFactory = Callable[[], CachePath]


@runtime_checkable
class KeyMaker(Protocol):
    """Protocol defining the interface for cache key generation."""

    def __call__(self, *args: Any, **kwargs: Any) -> CacheKey:
        """Generate a cache key from function arguments."""
        ...


@runtime_checkable
class Serializer(Protocol):
    """Protocol defining the interface for cache value serialization."""

    def dumps(self, obj: Any) -> bytes:
        """Serialize an object to bytes."""
        ...

    def loads(self, data: bytes) -> Any:
        """Deserialize bytes to an object."""
        ...


# Export all types
__all__ = [
    "BackendType",
    "CacheConfig",
    "CacheEngine",
    "CacheKey",
    "CachePath",
    "CachePathFactory",
    "CacheStats",
    "CacheValue",
    "F",
    "KeyMaker",
    "P",
    "R",
    "Serializer",
]

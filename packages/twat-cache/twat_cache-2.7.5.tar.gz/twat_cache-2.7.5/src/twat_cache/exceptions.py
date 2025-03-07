#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "loguru",
# ]
# ///
# this_file: src/twat_cache/exceptions.py

"""
Custom exceptions for the twat_cache package.

This module provides a hierarchy of exception classes for consistent error handling
across all components of the caching system.
"""

from typing import Any


class TwatCacheError(Exception):
    """Base exception for all twat_cache errors.

    All exceptions raised by the twat_cache package inherit from this base class,
    allowing for easier exception handling by users.
    """

    def __init__(self, message: str, *args: Any) -> None:
        """Initialize with an error message and optional additional arguments.

        Args:
            message: Descriptive error message
            *args: Additional arguments to pass to the Exception constructor
        """
        self.message = message
        super().__init__(message, *args)


class ConfigurationError(TwatCacheError):
    """Raised when there is an error in the cache configuration."""



class EngineError(TwatCacheError):
    """Base class for all engine-related errors."""



class EngineNotAvailableError(EngineError):
    """Raised when a requested cache engine is not available."""

    def __init__(self, message: str, reason: str | None = None) -> None:
        """Initialize with a message and an optional reason.

        Args:
            message: Error message
            reason: Optional reason why the engine is not available
        """
        if reason:
            message += f": {reason}"
        super().__init__(message)
        self.reason = reason


class CacheOperationError(TwatCacheError):
    """Raised when a cache operation fails."""



class CacheKeyError(CacheOperationError):
    """Raised when there is an issue with a cache key."""



class CacheValueError(CacheOperationError):
    """Raised when there is an issue with a cache value."""



class SerializationError(CacheOperationError):
    """Raised when serialization or deserialization fails."""



class ResourceError(TwatCacheError):
    """Raised when there is an issue with resource management."""



class ConcurrencyError(ResourceError):
    """Raised when there is a concurrency-related issue."""



class PathError(ResourceError):
    """Raised when there is an issue with cache paths."""


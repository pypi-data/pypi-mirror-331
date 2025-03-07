#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "loguru",
# ]
# ///
# this_file: src/twat_cache/engines/common.py

"""
Common utilities for cache engines.

This module provides shared functionality used by multiple cache engine
implementations to reduce code duplication and ensure consistent behavior.
"""

import inspect
import json
import os
import tempfile
from pathlib import Path
from typing import Any, TypeVar
from collections.abc import Callable

from loguru import logger

from twat_cache.exceptions import (
    CacheKeyError,
    CacheValueError,
    ResourceError,
    PathError,
)
from twat_cache.type_defs import CacheKey, P, R

# Type variable for cache key
K = TypeVar("K")
# Type variable for cache value
V = TypeVar("V")


def ensure_dir_exists(dir_path: Path, mode: int = 0o700) -> None:
    """
    Ensure a directory exists with proper permissions.

    Args:
        dir_path: Path to the directory to create if it doesn't exist
        mode: Permission mode for the directory (default is 0o700 for security)

    Raises:
        PathError: If directory cannot be created or permissions set
    """
    try:
        dir_path.mkdir(mode=mode, parents=True, exist_ok=True)
    except (OSError, PermissionError) as e:
        logger.error(f"Failed to create cache directory {dir_path}: {e}")
        msg = f"Failed to create cache directory {dir_path}: {e!s}"
        raise PathError(msg) from e


def safe_key_serializer(key: Any) -> str:
    """
    Safely serialize a cache key to a string.

    Args:
        key: Any object to use as a cache key

    Returns:
        A string representation of the key suitable for cache storage

    Raises:
        CacheKeyError: If key cannot be serialized
    """
    try:
        if isinstance(key, str):
            return key

        if isinstance(key, int | float | bool | type(None)):
            return str(key)

        if isinstance(key, list | tuple | set):
            return json.dumps([safe_key_serializer(k) for k in key])

        if isinstance(key, dict):
            return json.dumps({str(k): safe_key_serializer(v) for k, v in key.items()})

        # For other objects, use their repr (fallback)
        return json.dumps(repr(key))
    except Exception as e:
        logger.error(f"Failed to serialize cache key: {e}")
        msg = f"Failed to serialize cache key: {e!s}"
        raise CacheKeyError(msg) from e


def safe_value_serializer(value: Any) -> str:
    """
    Safely serialize a cache value to a string.

    Args:
        value: Any object to store in cache

    Returns:
        A string representation of the value suitable for cache storage

    Raises:
        CacheValueError: If value cannot be serialized
    """
    try:
        return json.dumps(value)
    except (TypeError, ValueError, OverflowError):
        try:
            # Fallback to repr for complex objects
            return repr(value)
        except Exception as inner_e:
            logger.error(f"Failed to serialize cache value: {inner_e}")
            msg = f"Failed to serialize cache value: {inner_e!s}"
            raise CacheValueError(
                msg
            ) from inner_e


def safe_temp_file(
    prefix: str = "twat_cache_", suffix: str = ".tmp"
) -> tuple[Path, Any]:
    """
    Safely create a temporary file with proper permissions.

    Args:
        prefix: Prefix for the temporary file name
        suffix: Suffix for the temporary file name

    Returns:
        A tuple of (file path, file object)

    Raises:
        ResourceError: If temporary file cannot be created
    """
    try:
        fd, path = tempfile.mkstemp(prefix=prefix, suffix=suffix)
        os.chmod(path, 0o600)  # Ensure secure permissions
        return Path(path), os.fdopen(fd, "w+b")
    except (OSError, PermissionError) as e:
        logger.error(f"Failed to create temporary file: {e}")
        msg = f"Failed to create temporary file: {e!s}"
        raise ResourceError(msg) from e


def get_func_qualified_name(func: Callable[..., Any]) -> str:
    """
    Get a qualified name for a function to use in cache naming.

    Args:
        func: The function to get a qualified name for

    Returns:
        A string containing the module and function name
    """
    module = inspect.getmodule(func)
    module_name = module.__name__ if module else "unknown_module"

    # Handle class methods and instance methods
    if hasattr(func, "__qualname__"):
        func_name = func.__qualname__
    else:
        func_name = func.__name__

    return f"{module_name}.{func_name}"


def create_cache_key(func: Callable[P, R], args: Any, kwargs: Any) -> CacheKey:
    """
    Create a consistent cache key from function and its arguments.

    Args:
        func: The function being cached
        args: Positional arguments to the function
        kwargs: Keyword arguments to the function

    Returns:
        A cache key suitable for most cache backends
    """
    # Get function's qualified name
    func_name = get_func_qualified_name(func)

    # Convert all arguments to a hashable form
    hashable_args = tuple(args)
    hashable_kwargs = tuple(sorted((k, v) for k, v in kwargs.items()))

    # Combine function name and arguments into a tuple
    return (func_name, hashable_args, hashable_kwargs)

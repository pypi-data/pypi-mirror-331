#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "loguru",
# ]
# ///
# this_file: src/twat_cache/utils.py

"""Utility functions for twat_cache."""

import json
from pathlib import Path
from typing import Any
from collections.abc import Callable


def get_cache_dir(folder_name: str | None = None) -> Path:
    """
    Get or create cache directory.

    Args:
        folder_name: Optional name for the cache folder

    Returns:
        Path to the cache directory

    Raises:
        ValueError: If folder_name contains invalid characters
        OSError: If directory creation fails
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


def make_key(
    serializer: Callable[[Any], str] | None = None, *args: Any, **kwargs: Any
) -> str:
    """
    Create a cache key from function arguments.

    Args:
        serializer: Optional function to serialize non-JSON-serializable objects
        *args: Positional arguments to include in key
        **kwargs: Keyword arguments to include in key

    Returns:
        A string key that uniquely identifies the arguments
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


# Alias for backward compatibility
get_cache_path = get_cache_dir

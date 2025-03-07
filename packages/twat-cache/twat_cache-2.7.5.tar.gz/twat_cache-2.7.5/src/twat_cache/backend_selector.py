#!/usr/bin/env -S uv run -s
# /// script
# dependencies = [
#   "loguru",
#   "pydantic",
# ]
# ///
# this_file: src/twat_cache/backend_selector.py

"""
Backend selector for twat_cache.

This module provides utilities for automatically selecting the most appropriate
cache backend based on data characteristics such as type, size, and access patterns.
It implements the strategy outlined in the project documentation for matching
data types to their optimal caching backends.
"""

import sys
from enum import Enum
from typing import Any, TypeVar, get_type_hints
from collections.abc import Callable
from collections.abc import Awaitable, Coroutine

from loguru import logger

from twat_cache.config import CacheConfig
from twat_cache.engines.base import is_package_available

# Type variables
F = TypeVar("F", bound=Callable[..., Any])
R = TypeVar("R")


class DataSize(Enum):
    """Enum representing different data size categories."""

    SMALL = "small"  # < 10KB
    MEDIUM = "medium"  # 10KB - 1MB
    LARGE = "large"  # 1MB - 100MB
    VERY_LARGE = "very_large"  # > 100MB


class DataPersistence(Enum):
    """Enum representing different data persistence requirements."""

    EPHEMERAL = "ephemeral"  # Only needed during program execution
    SESSION = "session"  # Needed across multiple runs in a session
    LONG_TERM = "long_term"  # Needed across multiple sessions/days


class AccessPattern(Enum):
    """Enum representing different data access patterns."""

    READ_HEAVY = "read_heavy"  # Data that is read frequently but written rarely
    WRITE_HEAVY = "write_heavy"  # Data that is updated frequently
    BALANCED = "balanced"  # Similar read and write frequencies
    TEMPORAL = "temporal"  # Data accessed in clusters over time
    FREQUENCY = "frequency"  # Data accessed based on frequency


class ConcurrencyLevel(Enum):
    """Enum representing different concurrency requirements."""

    SINGLE_THREAD = "single_thread"  # No concurrent access
    MULTI_THREAD = "multi_thread"  # Concurrent access from multiple threads
    MULTI_PROCESS = "multi_process"  # Concurrent access from multiple processes
    DISTRIBUTED = "distributed"  # Concurrent access from multiple machines


# Backend preference mappings
TYPE_TO_BACKEND = {
    # Simple Python types
    int: "cachetools",
    float: "cachetools",
    str: "cachetools",
    bool: "cachetools",
    # Collections
    list: "cachetools",
    dict: "cachetools",
    set: "cachetools",
    tuple: "cachetools",
    # Special handling for specific types
    "numpy.ndarray": "joblib",
    "pandas.DataFrame": "joblib",
    "pandas.Series": "joblib",
    "PIL.Image.Image": "diskcache",
    "torch.Tensor": "joblib",
    "tensorflow.Tensor": "joblib",
    # Default for custom classes
    object: "klepto",
    # Async types
    Awaitable: "aiocache",
    Coroutine: "aiocache",
}

# Alternative backends when preferred is not available
ALTERNATIVE_BACKENDS = {
    "cachetools": ["functools", "klepto", "diskcache"],
    "functools": ["cachetools", "klepto"],
    "joblib": ["diskcache", "klepto"],
    "diskcache": ["klepto", "joblib"],
    "klepto": ["diskcache", "cachetools"],
    "aiocache": ["cachetools", "functools"],
    "cachebox": ["cachetools", "diskcache"],
}

# Size-based backend selection
SIZE_TO_BACKEND = {
    DataSize.SMALL: "cachetools",
    DataSize.MEDIUM: "klepto",
    DataSize.LARGE: "diskcache",
    DataSize.VERY_LARGE: "joblib",
}

# Persistence-based backend selection
PERSISTENCE_TO_BACKEND = {
    DataPersistence.EPHEMERAL: "cachetools",
    DataPersistence.SESSION: "klepto",
    DataPersistence.LONG_TERM: "diskcache",
}

# Access pattern-based backend selection
ACCESS_TO_BACKEND = {
    AccessPattern.READ_HEAVY: "cachetools",  # with LRU policy
    AccessPattern.WRITE_HEAVY: "cachetools",  # with small maxsize
    AccessPattern.BALANCED: "diskcache",
    AccessPattern.TEMPORAL: "cachetools",  # with LRU policy
    AccessPattern.FREQUENCY: "klepto",  # with LFU policy
}

# Concurrency-based backend selection
CONCURRENCY_TO_BACKEND = {
    ConcurrencyLevel.SINGLE_THREAD: "cachetools",
    ConcurrencyLevel.MULTI_THREAD: "cachetools",
    ConcurrencyLevel.MULTI_PROCESS: "diskcache",
    ConcurrencyLevel.DISTRIBUTED: "diskcache",
}

# Size thresholds in bytes
SIZE_THRESHOLDS = {
    DataSize.SMALL: 10 * 1024,  # 10KB
    DataSize.MEDIUM: 1024 * 1024,  # 1MB
    DataSize.LARGE: 100 * 1024 * 1024,  # 100MB
}


def estimate_data_size(data: Any) -> DataSize:
    """
    Estimate the size category of a data object.

    Args:
        data: The data object to analyze

    Returns:
        DataSize: The estimated size category
    """
    try:
        # Try to get the size using sys.getsizeof
        size = sys.getsizeof(data)

        # For certain types, we need to account for nested objects
        if isinstance(data, list | tuple | set | dict):
            # Add approximate size of contents for containers
            if isinstance(data, list | tuple | set):
                for item in data:
                    size += sys.getsizeof(item)
            elif isinstance(data, dict):
                for key, value in data.items():
                    size += sys.getsizeof(key) + sys.getsizeof(value)

        # Determine size category
        if size < SIZE_THRESHOLDS[DataSize.SMALL]:
            return DataSize.SMALL
        elif size < SIZE_THRESHOLDS[DataSize.MEDIUM]:
            return DataSize.MEDIUM
        elif size < SIZE_THRESHOLDS[DataSize.LARGE]:
            return DataSize.LARGE
        else:
            return DataSize.VERY_LARGE

    except (TypeError, AttributeError):
        # If we can't determine size, default to MEDIUM
        return DataSize.MEDIUM


def get_type_based_backend(data_type: type) -> str:
    """
    Get the recommended backend based on data type.

    Args:
        data_type: The type of data to be cached

    Returns:
        str: The recommended backend name
    """
    # Check for exact type match
    if data_type in TYPE_TO_BACKEND:
        return TYPE_TO_BACKEND[data_type]

    # Check for special types by name (for types that might not be imported)
    type_name = f"{data_type.__module__}.{data_type.__name__}"
    for special_type, backend in TYPE_TO_BACKEND.items():
        if isinstance(special_type, str) and special_type == type_name:
            return backend

    # Check for subclass relationships
    for base_type, backend in TYPE_TO_BACKEND.items():
        if not isinstance(base_type, str) and issubclass(data_type, base_type):
            return backend

    # Default to object's backend if no match found
    return TYPE_TO_BACKEND[object]


def get_available_backend(preferred_backend: str) -> str:
    """
    Get an available backend, starting with the preferred one.

    Args:
        preferred_backend: The preferred backend name

    Returns:
        str: The name of an available backend
    """
    # Check if preferred backend is available
    if is_backend_available(preferred_backend):
        return preferred_backend

    # Try alternatives
    for alt_backend in ALTERNATIVE_BACKENDS.get(preferred_backend, []):
        if is_backend_available(alt_backend):
            logger.debug(f"Preferred backend '{preferred_backend}' not available, using '{alt_backend}' instead")
            return alt_backend

    # If no alternatives are available, default to functools which is always available
    logger.debug("No suitable backend found, defaulting to 'functools'")
    return "functools"


def is_backend_available(backend_name: str) -> bool:
    """
    Check if a backend is available.

    Args:
        backend_name: The name of the backend to check

    Returns:
        bool: True if the backend is available, False otherwise
    """
    # functools is always available
    if backend_name == "functools":
        return True

    # Map backend names to their package requirements
    package_map = {
        "cachetools": "cachetools",
        "diskcache": "diskcache",
        "joblib": "joblib",
        "klepto": "klepto",
        "aiocache": "aiocache",
        "cachebox": "cachebox",
    }

    # Check if the required package is available
    package_name = package_map.get(backend_name)
    if package_name:
        return is_package_available(package_name)

    return False


def select_backend_for_data(
    data: Any = None,
    data_type: type | None = None,
    size: DataSize = None,
    persistence: DataPersistence = None,
    access_pattern: AccessPattern = None,
    concurrency: ConcurrencyLevel = None,
    config: CacheConfig = None,
) -> str:
    """
    Select the most appropriate backend based on data characteristics.

    Args:
        data: Sample data (used to infer characteristics if not explicitly provided)
        data_type: The type of data to be cached
        size: The size category of the data
        persistence: The persistence requirements
        access_pattern: The access pattern for the data
        concurrency: The concurrency requirements
        config: Existing cache configuration to consider

    Returns:
        str: The name of the selected backend
    """
    # Priority order for backend selection
    backends = []

    # 1. Use explicit config if provided
    if config and config.preferred_engine:
        backends.append(config.preferred_engine)

    # 2. Use data type if provided or inferred
    if data_type is None and data is not None:
        data_type = type(data)

    if data_type is not None:
        backends.append(get_type_based_backend(data_type))

    # 3. Use size if provided or inferred
    if size is None and data is not None:
        size = estimate_data_size(data)

    if size is not None:
        backends.append(SIZE_TO_BACKEND[size])

    # 4. Use persistence if provided
    if persistence is not None:
        backends.append(PERSISTENCE_TO_BACKEND[persistence])

    # 5. Use access pattern if provided
    if access_pattern is not None:
        backends.append(ACCESS_TO_BACKEND[access_pattern])

    # 6. Use concurrency if provided
    if concurrency is not None:
        backends.append(CONCURRENCY_TO_BACKEND[concurrency])

    # 7. Default to cachetools if nothing else is specified
    backends.append("cachetools")

    # Try each backend in order until we find one that's available
    for backend in backends:
        available_backend = get_available_backend(backend)
        if available_backend:
            return available_backend

    # This should never happen since functools is always available
    return "functools"


def configure_for_type(data_type: type, **kwargs) -> CacheConfig:
    """
    Create a cache configuration optimized for a specific data type.

    Args:
        data_type: The type of data to be cached
        **kwargs: Additional configuration parameters

    Returns:
        CacheConfig: A cache configuration optimized for the data type
    """
    backend = get_type_based_backend(data_type)
    available_backend = get_available_backend(backend)

    # Start with default configuration
    config_params = {
        "preferred_engine": available_backend,
    }

    # Add type-specific optimizations
    if available_backend == "cachetools":
        config_params["maxsize"] = 128
        config_params["policy"] = "lru"
    elif available_backend == "diskcache":
        config_params["compress"] = True
        config_params["folder_name"] = f"{data_type.__name__.lower()}_cache"
    elif available_backend == "joblib":
        config_params["folder_name"] = f"{data_type.__name__.lower()}_joblib"

    # Override with any provided kwargs
    config_params.update(kwargs)

    return CacheConfig(**config_params)


def configure_for_numpy() -> CacheConfig:
    """
    Create a cache configuration optimized for NumPy arrays.

    Returns:
        CacheConfig: A cache configuration optimized for NumPy arrays
    """
    # Try to import numpy to check if it's available
    try:
        import numpy as np

        return configure_for_type(np.ndarray, folder_name="numpy_cache")
    except ImportError:
        # If numpy is not available, return a generic configuration
        logger.warning("NumPy not available, returning generic configuration")
        return CacheConfig(preferred_engine=get_available_backend("joblib"))


def configure_for_pandas() -> CacheConfig:
    """
    Create a cache configuration optimized for pandas DataFrames.

    Returns:
        CacheConfig: A cache configuration optimized for pandas DataFrames
    """
    try:
        import pandas as pd

        return configure_for_type(pd.DataFrame, folder_name="pandas_cache")
    except ImportError:
        logger.warning("Pandas not available, returning generic configuration")
        return CacheConfig(preferred_engine=get_available_backend("joblib"))


def configure_for_images() -> CacheConfig:
    """
    Create a cache configuration optimized for image data.

    Returns:
        CacheConfig: A cache configuration optimized for image data
    """
    return CacheConfig(
        preferred_engine=get_available_backend("diskcache"),
        folder_name="image_cache",
        compress=True,
    )


def configure_for_json() -> CacheConfig:
    """
    Create a cache configuration optimized for JSON data.

    Returns:
        CacheConfig: A cache configuration optimized for JSON data
    """
    return CacheConfig(
        preferred_engine=get_available_backend("diskcache"),
        folder_name="json_cache",
        compress=True,
    )


def hybrid_cache_config(
    small_result_engine: str = "cachetools",
    large_result_engine: str = "diskcache",
    size_threshold: int = 1024 * 1024,  # 1MB
    **kwargs,
) -> dict[str, Any]:
    """
    Create a configuration for hybrid caching based on result size.

    This doesn't return a CacheConfig directly, as it's meant to be used
    with a special decorator that switches backends based on result size.

    Args:
        small_result_engine: Backend to use for small results
        large_result_engine: Backend to use for large results
        size_threshold: Size threshold in bytes
        **kwargs: Additional configuration parameters

    Returns:
        Dict[str, Any]: Configuration dictionary for hybrid caching
    """
    return {
        "small_result_engine": get_available_backend(small_result_engine),
        "large_result_engine": get_available_backend(large_result_engine),
        "size_threshold": size_threshold,
        **kwargs,
    }


def analyze_function_return_type(func: Callable) -> type | None:
    """
    Analyze a function to determine its return type.

    Args:
        func: The function to analyze

    Returns:
        Optional[Type]: The return type if it can be determined, None otherwise
    """
    # Try to get type hints
    try:
        hints = get_type_hints(func)
        if "return" in hints:
            return hints["return"]
    except (TypeError, ValueError):
        pass

    # If no type hints, return None
    return None


def smart_cache_config(func: F = None, **kwargs) -> CacheConfig:
    """
    Create a smart cache configuration based on function analysis.

    Args:
        func: The function to analyze
        **kwargs: Additional configuration parameters

    Returns:
        CacheConfig: A smart cache configuration
    """
    config_params = {}

    # If function is provided, analyze its return type
    if func is not None:
        return_type = analyze_function_return_type(func)
        if return_type is not None:
            # Get backend based on return type
            backend = get_type_based_backend(return_type)
            config_params["preferred_engine"] = get_available_backend(backend)

    # Override with any provided kwargs
    config_params.update(kwargs)

    return CacheConfig(**config_params)


# Runtime type detection wrapper (for use with hybrid caching)
def detect_result_type(result: Any) -> str:
    """
    Detect the appropriate backend for a result at runtime.

    Args:
        result: The result to analyze

    Returns:
        str: The name of the appropriate backend
    """
    return select_backend_for_data(data=result)

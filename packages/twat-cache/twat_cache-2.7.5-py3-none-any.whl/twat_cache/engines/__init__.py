#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "loguru",
# ]
# ///
# this_file: src/twat_cache/engines/__init__.py

"""
Cache engine implementations.

This package provides various cache engine implementations for different
backends and use cases.
"""

from typing import Dict, List, Type, Any, cast

from .base import BaseCacheEngine, is_package_available
from .manager import get_engine_manager

# Optional imports - these may fail if dependencies are not installed
engines: dict[str, type[BaseCacheEngine[Any, Any]]] = {}

try:
    from .functools import FunctoolsCacheEngine

    engines["functools"] = cast(type[BaseCacheEngine[Any, Any]], FunctoolsCacheEngine)
except ImportError:
    pass

try:
    from .cachetools import CacheToolsEngine

    engines["cachetools"] = cast(type[BaseCacheEngine[Any, Any]], CacheToolsEngine)
except ImportError:
    pass

try:
    from .diskcache import DiskCacheEngine

    engines["diskcache"] = cast(type[BaseCacheEngine[Any, Any]], DiskCacheEngine)
except ImportError:
    pass

try:
    from .aiocache import AioCacheEngine

    engines["aiocache"] = cast(type[BaseCacheEngine[Any, Any]], AioCacheEngine)
except ImportError:
    pass

try:
    from .klepto import KleptoEngine

    engines["klepto"] = cast(type[BaseCacheEngine[Any, Any]], KleptoEngine)
except ImportError:
    pass

try:
    from .joblib import JoblibEngine

    engines["joblib"] = cast(type[BaseCacheEngine[Any, Any]], JoblibEngine)
except ImportError:
    pass

try:
    from .cachebox import CacheBoxEngine

    engines["cachebox"] = cast(type[BaseCacheEngine[Any, Any]], CacheBoxEngine)
except ImportError:
    pass

try:
    from .redis import RedisCacheEngine

    engines["redis"] = cast(type[BaseCacheEngine[Any, Any]], RedisCacheEngine)
except ImportError:
    pass


def get_available_engines() -> list[str]:
    """
    Get a list of available cache engines.

    Returns:
        List of available engine names.
    """
    return [
        name
        for name, engine_cls in engines.items()
        if hasattr(engine_cls, "is_available") and engine_cls.is_available()
    ]


__all__ = [
    "BaseCacheEngine",
    "get_available_engines",
    "get_engine_manager",
    "is_package_available",
]

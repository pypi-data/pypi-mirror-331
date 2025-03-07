"""Flexible caching utilities for Python functions with multiple high-performance backends."""

# this_file: src/twat_cache/__init__.py

from twat_cache.cache import clear_cache, get_stats
from twat_cache.decorators import bcache, fcache, mcache, ucache
from twat_cache.utils import get_cache_path
from twat_cache.context import engine_context, CacheContext, get_or_create_engine
from twat_cache.exceptions import (
    TwatCacheError,
    ConfigurationError,
    EngineError,
    EngineNotAvailableError,
    CacheOperationError,
    CacheKeyError,
    CacheValueError,
    SerializationError,
    ResourceError,
    ConcurrencyError,
    PathError,
)

# Import new modules
from twat_cache.backend_selector import (
    configure_for_numpy,
    configure_for_pandas,
    configure_for_images,
    configure_for_json,
    configure_for_type,
    select_backend_for_data,
    DataSize,
    DataPersistence,
    AccessPattern,
    ConcurrencyLevel,
)
from twat_cache.hybrid_cache import hybrid_cache, smart_cache

try:
    from twat_cache.__version__ import __version__
except ImportError:
    __version__ = "0.0.0"

__all__ = [
    "AccessPattern",
    "CacheContext",
    "CacheKeyError",
    "CacheOperationError",
    "CacheValueError",
    "ConcurrencyError",
    "ConcurrencyLevel",
    "ConfigurationError",
    "DataPersistence",
    "DataSize",
    "EngineError",
    "EngineNotAvailableError",
    "PathError",
    "ResourceError",
    "SerializationError",
    # Exceptions
    "TwatCacheError",
    "__version__",
    "bcache",
    "clear_cache",
    "configure_for_images",
    "configure_for_json",
    # New backend selection utilities
    "configure_for_numpy",
    "configure_for_pandas",
    "configure_for_type",
    # Context management
    "engine_context",
    "fcache",
    "get_cache_path",
    "get_or_create_engine",
    "get_stats",
    # New hybrid caching utilities
    "hybrid_cache",
    "mcache",
    "select_backend_for_data",
    "smart_cache",
    "ucache",
]

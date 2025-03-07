#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "loguru",
#   "aiocache",
#   "diskcache",
# ]
# ///
# this_file: src/twat_cache/engines/manager.py

"""
Cache engine manager module.

This module provides the CacheEngineManager class which handles registration,
selection and management of cache engine implementations.
"""

from typing import Any, TypeVar, cast

from loguru import logger

from twat_cache.type_defs import (
    CacheConfig,
)
from .aiocache import AioCacheEngine
from .base import BaseCacheEngine
from .cachebox import CacheBoxEngine
from .cachetools import CacheToolsEngine
from .diskcache import DiskCacheEngine
from .functools import FunctoolsCacheEngine
from .joblib import JoblibEngine
from .klepto import KleptoEngine

# Type variable for concrete cache engine
E = TypeVar("E", bound=BaseCacheEngine[Any, Any])

# Try to import optional backends
try:
    from .aiocache import AioCacheEngine

    HAS_AIOCACHE = True
except ImportError:
    HAS_AIOCACHE = False
    logger.debug("aiocache not available")

try:
    from .cachetools import CacheToolsEngine

    HAS_CACHETOOLS = True
except ImportError:
    HAS_CACHETOOLS = False
    logger.debug("cachetools not available")

try:
    from .klepto import KleptoEngine

    HAS_KLEPTO = True
except ImportError:
    HAS_KLEPTO = False
    logger.debug("klepto not available")

try:
    from .joblib import JoblibEngine

    HAS_JOBLIB = True
except ImportError:
    HAS_JOBLIB = False
    logger.debug("joblib not available")

try:
    from .redis import RedisCacheEngine

    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    logger.debug("redis not available")


class CacheEngineManager:
    """Manages cache engine implementations and handles engine selection."""

    def __init__(self) -> None:
        """Initialize the cache engine manager."""
        self._engines: dict[str, type[BaseCacheEngine[Any, Any]]] = {}
        self._register_builtin_engines()

    def _register_builtin_engines(self) -> None:
        """Register built-in cache engine implementations."""
        self.register_engine("functools", FunctoolsCacheEngine)
        self.register_engine("cachetools", CacheToolsEngine)
        self.register_engine("diskcache", DiskCacheEngine)
        self.register_engine("aiocache", AioCacheEngine)
        self.register_engine("klepto", KleptoEngine)
        self.register_engine("joblib", JoblibEngine)
        self.register_engine("cachebox", CacheBoxEngine)

        # Register Redis engine if available
        if HAS_REDIS:
            self.register_engine("redis", RedisCacheEngine)

    def register_engine(self, name: str, engine_cls: type[E]) -> None:
        """
        Register a new cache engine implementation.

        Args:
            name: Unique name for the engine
            engine_cls: Cache engine class to register
        """
        if name in self._engines:
            logger.warning(f"Overwriting existing engine registration for {name}")
        self._engines[name] = cast(type[BaseCacheEngine[Any, Any]], engine_cls)

    def get_engine(self, name: str) -> type[BaseCacheEngine[Any, Any]] | None:
        """
        Get a registered cache engine by name.

        Args:
            name: Name of the engine to retrieve

        Returns:
            The cache engine class if found, None otherwise
        """
        return self._engines.get(name)

    def list_engines(self) -> list[str]:
        """
        Get a list of all registered engine names.

        Returns:
            List of registered engine names
        """
        return list(self._engines.keys())

    def get_available_engines(self) -> list[str]:
        """
        Get a list of registered engines that are available for use.

        Returns:
            List of available engine names
        """
        return [name for name, engine in self._engines.items() if engine.is_available()]

    def select_engine(
        self,
        config: CacheConfig,
        preferred: list[str] | None = None,
    ) -> type[BaseCacheEngine[Any, Any]] | None:
        """
        Select an appropriate cache engine based on configuration and preferences.

        Args:
            config: Cache configuration
            preferred: List of preferred engine names in priority order

        Returns:
            Selected cache engine class or None if no suitable engine is found
        """
        available = self.get_available_engines()

        if not available:
            logger.warning("No cache engines are available")
            return None

        if preferred:
            # Try preferred engines in order
            for engine_name in preferred:
                if engine_name in available:
                    engine_cls: type[BaseCacheEngine[Any, Any]] | None = self.get_engine(engine_name)
                    if engine_cls and engine_cls.is_available():
                        return engine_cls

        # Fall back to first available engine
        fallback: type[BaseCacheEngine[Any, Any]] | None = self.get_engine(available[0])
        if fallback and fallback.is_available():
            return fallback

        return None


def get_engine_manager() -> CacheEngineManager:
    """
    Get the global engine manager instance.

    Returns:
        The global engine manager instance
    """
    return CacheEngineManager()

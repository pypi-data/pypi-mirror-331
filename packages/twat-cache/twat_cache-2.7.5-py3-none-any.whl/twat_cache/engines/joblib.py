"""Joblib-based cache engine implementation."""

from __future__ import annotations

from typing import cast

from twat_cache.engines.base import BaseCacheEngine
from twat_cache.type_defs import F, CacheKey, P, R
from twat_cache.paths import get_cache_path
from twat_cache.config import CacheConfig


class DummyMemory:
    """Dummy implementation of joblib.Memory for when joblib is not available."""

    def cache(self, func: F) -> F:
        return func

    def clear(self) -> None:
        pass


try:
    from joblib.memory import Memory as JoblibMemory

    HAS_JOBLIB = True
except ImportError:
    JoblibMemory = DummyMemory  # type: ignore
    HAS_JOBLIB = False


class JoblibEngine(BaseCacheEngine[P, R]):
    """Cache engine using joblib for disk caching of numpy arrays and large objects."""

    def __init__(self, config: CacheConfig) -> None:
        """Initialize joblib cache engine.

        Args:
            config: Cache configuration.
        """
        super().__init__(config)
        folder_name = getattr(self._config, "folder_name", None)
        self._folder_name = folder_name or "joblib"
        self._memory = (
            JoblibMemory(str(get_cache_path(self._folder_name)), verbose=0)
            if HAS_JOBLIB
            else DummyMemory()
        )

    def _get_cached_value(self, key: CacheKey) -> R | None:
        """Retrieve a value from the cache.

        Joblib doesn't have a direct get-by-key method. We rely on its
        internal caching mechanism within the decorated function.
        """
        # Joblib's caching is handled within the decorated function itself.
        # We return None here to indicate that we haven't retrieved a value
        # directly. The actual cache lookup happens within the `cache` wrapper.
        _ = key  # Used for type checking
        return None

    def _set_cached_value(self, key: CacheKey, value: R) -> None:
        """Store a value in the cache.

        Joblib doesn't have a direct set-by-key method.  The caching happens
        implicitly when the decorated function is called.
        """
        # Joblib's caching is handled within the decorated function itself.
        # We don't need to do anything here.
        _ = key, value  # Used for type checking

    def clear(self) -> None:
        """Clear all cached values."""
        self._memory.clear()

    @classmethod
    def is_available(cls) -> bool:
        """Check if joblib is available."""
        return HAS_JOBLIB

    @property
    def name(self) -> str:
        """Get engine name."""
        return "joblib"

    def cache(self, func: F) -> F:
        """Apply joblib caching to the function.

        Args:
            func: Function to be cached

        Returns:
            Cached function wrapper
        """
        return cast(F, self._memory.cache(func))

#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "pytest",
#   "loguru",
# ]
# ///
# this_file: tests/test_exceptions_simple.py

"""Simple test suite for twat_cache exception handling."""

import pytest

# Import exceptions directly
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


def test_exception_hierarchy():
    """Test that the exception hierarchy is correctly set up."""
    # Base exception
    assert issubclass(TwatCacheError, Exception)

    # Second-level exceptions
    assert issubclass(ConfigurationError, TwatCacheError)
    assert issubclass(EngineError, TwatCacheError)
    assert issubclass(CacheOperationError, TwatCacheError)
    assert issubclass(ResourceError, TwatCacheError)

    # Third-level exceptions
    assert issubclass(EngineNotAvailableError, EngineError)
    assert issubclass(CacheKeyError, CacheOperationError)
    assert issubclass(CacheValueError, CacheOperationError)
    assert issubclass(SerializationError, CacheOperationError)
    assert issubclass(ConcurrencyError, ResourceError)
    assert issubclass(PathError, ResourceError)


def test_exception_messages():
    """Test that exceptions can be instantiated with messages."""
    # Base exception
    base_exc = TwatCacheError("Base error message")
    assert str(base_exc) == "Base error message"

    # Second-level exceptions
    config_exc = ConfigurationError("Configuration error message")
    assert str(config_exc) == "Configuration error message"

    engine_exc = EngineError("Engine error message")
    assert str(engine_exc) == "Engine error message"

    operation_exc = CacheOperationError("Operation error message")
    assert str(operation_exc) == "Operation error message"

    resource_exc = ResourceError("Resource error message")
    assert str(resource_exc) == "Resource error message"

    # Third-level exceptions
    engine_not_available_exc = EngineNotAvailableError("Engine not available message")
    assert str(engine_not_available_exc) == "Engine not available message"

    key_exc = CacheKeyError("Key error message")
    assert str(key_exc) == "Key error message"

    value_exc = CacheValueError("Value error message")
    assert str(value_exc) == "Value error message"

    serialization_exc = SerializationError("Serialization error message")
    assert str(serialization_exc) == "Serialization error message"

    concurrency_exc = ConcurrencyError("Concurrency error message")
    assert str(concurrency_exc) == "Concurrency error message"

    path_exc = PathError("Path error message")
    assert str(path_exc) == "Path error message"


if __name__ == "__main__":
    pytest.main(["-v", __file__])

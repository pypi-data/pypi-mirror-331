#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "pytest",
#   "loguru",
# ]
# ///
# this_file: tests/test_exceptions.py

"""Test suite for twat_cache exception handling."""

import os
import tempfile
from pathlib import Path

import pytest

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
from twat_cache.engines.common import (
    ensure_dir_exists,
    safe_key_serializer,
    safe_value_serializer,
    safe_temp_file,
)


def test_base_exception():
    """Test the base exception class."""
    # Test basic exception
    exc = TwatCacheError("Test error message")
    assert str(exc) == "Test error message"
    assert exc.message == "Test error message"

    # Test with additional arguments
    exc = TwatCacheError("Test error message", "arg1", "arg2")
    assert str(exc) == "('Test error message', 'arg1', 'arg2')"
    assert exc.message == "Test error message"


def test_exception_hierarchy():
    """Test the exception inheritance hierarchy."""
    # Test that all exceptions inherit from TwatCacheError
    assert issubclass(ConfigurationError, TwatCacheError)
    assert issubclass(EngineError, TwatCacheError)
    assert issubclass(EngineNotAvailableError, EngineError)
    assert issubclass(CacheOperationError, TwatCacheError)
    assert issubclass(CacheKeyError, CacheOperationError)
    assert issubclass(CacheValueError, CacheOperationError)
    assert issubclass(SerializationError, TwatCacheError)
    assert issubclass(ResourceError, TwatCacheError)
    assert issubclass(ConcurrencyError, TwatCacheError)
    assert issubclass(PathError, TwatCacheError)


def test_engine_not_available_error():
    """Test the EngineNotAvailableError exception."""
    # Test with engine name only
    exc = EngineNotAvailableError("test_engine")
    assert str(exc) == "Cache engine 'test_engine' is not available"
    assert exc.engine_name == "test_engine"
    assert exc.reason is None

    # Test with engine name and reason
    exc = EngineNotAvailableError("test_engine", "Not installed")
    assert str(exc) == "Cache engine 'test_engine' is not available: Not installed"
    assert exc.engine_name == "test_engine"
    assert exc.reason == "Not installed"


def test_ensure_dir_exists():
    """Test the ensure_dir_exists function."""
    # Test creating a directory that doesn't exist
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir) / "test_dir"
        ensure_dir_exists(test_dir)
        assert test_dir.exists()
        assert test_dir.is_dir()

        # Test permissions
        if os.name != "nt":  # Skip on Windows
            assert (test_dir.stat().st_mode & 0o777) == 0o700

        # Test with custom permissions
        test_dir2 = Path(temp_dir) / "test_dir2"
        ensure_dir_exists(test_dir2, mode=0o755)
        assert test_dir2.exists()
        if os.name != "nt":  # Skip on Windows
            assert (test_dir2.stat().st_mode & 0o777) == 0o755


def test_ensure_dir_exists_error():
    """Test error handling in ensure_dir_exists."""
    # Create a file that will conflict with directory creation
    with tempfile.NamedTemporaryFile() as temp_file:
        # Try to create a directory with the same name as the file
        with pytest.raises(PathError) as excinfo:
            ensure_dir_exists(Path(temp_file.name))

        assert "Failed to create cache directory" in str(excinfo.value)


def test_safe_key_serializer():
    """Test the safe_key_serializer function."""
    # Test with simple types
    assert safe_key_serializer("test") == "test"
    assert safe_key_serializer(123) == "123"
    assert safe_key_serializer(True) == "True"
    assert safe_key_serializer(None) == "None"

    # Test with complex types
    assert safe_key_serializer([1, 2, 3]) == '["1", "2", "3"]'
    assert safe_key_serializer({"a": 1, "b": 2}) == '{"a": "1", "b": "2"}'

    # Test with nested types
    assert safe_key_serializer([1, {"a": 2}]) == '["1", {"a": "2"}]'


def test_safe_key_serializer_error():
    """Test error handling in safe_key_serializer."""

    # Create a class that raises an error when serialized
    class UnserializableObject:
        def __repr__(self):
            msg = "Cannot serialize"
            raise RuntimeError(msg)

    # Test with an unserializable object
    with pytest.raises(CacheKeyError) as excinfo:
        safe_key_serializer(UnserializableObject())

    assert "Failed to serialize cache key" in str(excinfo.value)


def test_safe_value_serializer():
    """Test the safe_value_serializer function."""
    # Test with simple values
    assert safe_value_serializer("test") == '"test"'
    assert safe_value_serializer(123) == "123"
    assert safe_value_serializer([1, 2, 3]) == "[1, 2, 3]"
    assert safe_value_serializer({"a": 1, "b": 2}) == '{"a": 1, "b": 2}'


def test_safe_value_serializer_error():
    """Test error handling in safe_value_serializer."""

    # Create an object that can't be JSON serialized
    class CustomObject:
        pass

    # This should not raise but fall back to repr
    result = safe_value_serializer(CustomObject())
    assert result.startswith("<")

    # Create a class that raises an error even with repr
    class BadObject:
        def __repr__(self):
            msg = "Cannot serialize"
            raise RuntimeError(msg)

    # This should raise a CacheValueError
    with pytest.raises(CacheValueError) as excinfo:
        safe_value_serializer(BadObject())

    assert "Failed to serialize cache value" in str(excinfo.value)


def test_safe_temp_file():
    """Test the safe_temp_file function."""
    # Test creating a temporary file
    path, file_obj = safe_temp_file()

    try:
        # Check that the file exists
        assert path.exists()
        assert path.is_file()

        # Check that we can write to it
        file_obj.write(b"test data")
        file_obj.flush()

        # Check permissions
        if os.name != "nt":  # Skip on Windows
            assert (path.stat().st_mode & 0o777) == 0o600

    finally:
        # Clean up
        file_obj.close()
        if path.exists():
            path.unlink()


def test_catching_exceptions():
    """Test catching the custom exceptions."""
    try:
        msg = "Test config error"
        raise ConfigurationError(msg)
    except TwatCacheError as e:
        assert isinstance(e, ConfigurationError)
        assert str(e) == "Test config error"

    try:
        msg = "test_engine"
        raise EngineNotAvailableError(msg, "Not installed")
    except EngineError as e:
        assert isinstance(e, EngineNotAvailableError)
        assert e.engine_name == "test_engine"
        assert e.reason == "Not installed"

    try:
        msg = "Invalid key"
        raise CacheKeyError(msg)
    except CacheOperationError as e:
        assert isinstance(e, CacheKeyError)
        assert str(e) == "Invalid key"

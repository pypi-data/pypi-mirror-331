#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "pytest",
#   "loguru",
# ]
# ///
# this_file: tests/test_context.py

"""Test suite for twat_cache context management."""

import tempfile

import pytest

from twat_cache.context import engine_context, CacheContext, get_or_create_engine
from twat_cache.exceptions import EngineError
from twat_cache.config import create_cache_config
from twat_cache.engines.base import BaseCacheEngine


def test_engine_context():
    """Test the engine_context context manager."""
    # Create a temporary directory for the cache
    with tempfile.TemporaryDirectory() as temp_dir:
        # Use the context manager with folder_name
        with engine_context(folder_name=temp_dir) as engine:
            # Check that we have an engine
            assert isinstance(engine, BaseCacheEngine)

            # Cache a simple function
            @engine.cache
            def add(x, y):
                return x + y

            # Call the function
            result = add(2, 3)
            assert result == 5

            # Call it again to use the cache
            result = add(2, 3)
            assert result == 5

            # Check that hits increased
            assert engine._hits == 1

        # Context manager should have cleaned up the engine


def test_engine_context_with_error():
    """Test that the context manager cleans up even when an error occurs."""
    # Create a temporary directory for the cache
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            with engine_context(folder_name=temp_dir) as engine:
                # Check that we have an engine
                assert isinstance(engine, BaseCacheEngine)

                # Deliberately raise an error
                msg = "Test error"
                raise ValueError(msg)
        except ValueError:
            # The exception should have propagated
            pass

        # Context manager should have cleaned up the engine regardless


def test_engine_context_with_invalid_engine():
    """Test that the context manager raises an error for invalid engines."""
    with pytest.raises(EngineError):
        with engine_context(engine_name="non_existent_engine"):
            pass  # This should not be executed


def test_cache_context_class():
    """Test the CacheContext class."""
    # Create a temporary directory for the cache
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a CacheContext instance
        context = CacheContext(folder_name=temp_dir)

        # Enter the context
        with context as engine:
            # Check that we have an engine
            assert isinstance(engine, BaseCacheEngine)

            # Cache a simple function
            @engine.cache
            def multiply(x, y):
                return x * y

            # Call the function
            result = multiply(2, 3)
            assert result == 6

            # Call it again to use the cache
            result = multiply(2, 3)
            assert result == 6

            # Check that hits increased
            assert engine._hits == 1

        # Context manager should have cleaned up the engine
        assert context.engine is None


def test_get_or_create_engine():
    """Test the get_or_create_engine function."""
    # Create a temporary directory for the cache
    with tempfile.TemporaryDirectory() as temp_dir:
        # Get an engine
        engine = get_or_create_engine(folder_name=temp_dir)

        try:
            # Check that we have an engine
            assert isinstance(engine, BaseCacheEngine)

            # Cache a simple function
            @engine.cache
            def divide(x, y):
                return x / y

            # Call the function
            result = divide(6, 3)
            assert result == 2

            # Call it again to use the cache
            result = divide(6, 3)
            assert result == 2

            # Check that hits increased
            assert engine._hits == 1
        finally:
            # Manually clean up the engine
            engine.cleanup()


def test_nested_contexts():
    """Test nested context managers."""
    # Create temporary directories for the caches
    with tempfile.TemporaryDirectory() as temp_dir1:
        with tempfile.TemporaryDirectory() as temp_dir2:
            # Use nested context managers
            with engine_context(folder_name=temp_dir1) as engine1:
                with engine_context(folder_name=temp_dir2) as engine2:
                    # Check that we have different engines
                    assert engine1 is not engine2

                    # Cache simple functions
                    @engine1.cache
                    def add(x, y):
                        return x + y

                    @engine2.cache
                    def multiply(x, y):
                        return x * y

                    # Call the functions
                    assert add(2, 3) == 5
                    assert multiply(2, 3) == 6

                    # Call them again to use the cache
                    assert add(2, 3) == 5
                    assert multiply(2, 3) == 6

                    # Check that hits increased
                    assert engine1._hits == 1
                    assert engine2._hits == 1

                # Inner context manager should have cleaned up engine2

            # Outer context manager should have cleaned up engine1


def test_context_with_config():
    """Test context manager with a config object."""
    # Create a config object
    config = create_cache_config(
        maxsize=100,
        ttl=60,
        policy="lru",
    )

    # Use the context manager with the config
    with engine_context(config=config) as engine:
        # Check that the config was applied
        assert engine._config.maxsize == 100
        assert engine._config.ttl == 60
        assert engine._config.policy == "lru"

        # Cache a simple function
        @engine.cache
        def add(x, y):
            return x + y

        # Call the function
        result = add(2, 3)
        assert result == 5

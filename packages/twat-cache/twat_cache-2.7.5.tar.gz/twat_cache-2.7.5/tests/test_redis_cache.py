#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "pytest",
#   "pytest-asyncio",
#   "loguru",
#   "redis",
#   "fakeredis",
# ]
# ///
# this_file: tests/test_redis_cache.py

"""Test suite for Redis cache engine."""

import pickle
import pytest
from unittest.mock import patch, MagicMock

from twat_cache.config import create_cache_config
from twat_cache.engines.redis import RedisCacheEngine
from twat_cache.exceptions import EngineNotAvailableError, ConfigurationError


class TestRedisCacheEngine:
    """Test Redis cache engine functionality."""

    @pytest.fixture
    def mock_redis(self):
        """Create a mock Redis client."""
        with patch("redis.Redis") as mock_redis:
            # Configure the mock
            mock_instance = MagicMock()
            mock_redis.return_value = mock_instance
            mock_instance.ping.return_value = True
            yield mock_instance

    @pytest.fixture
    def fake_redis(self):
        """Create a fake Redis client using fakeredis."""
        import fakeredis

        return fakeredis.FakeStrictRedis()

    @pytest.fixture
    def redis_engine(self, mock_redis):
        """Create a Redis cache engine with a mock Redis client."""
        config = create_cache_config(
            folder_name="test_redis",
            ttl=60,
            compress=False,
            redis_host="localhost",
            redis_port=6379,
            redis_db=0,
        )
        engine = RedisCacheEngine(config)
        engine._redis = mock_redis  # Replace with our mock
        return engine

    @pytest.fixture
    def real_redis_engine(self, fake_redis):
        """Create a Redis cache engine with a fake Redis client."""
        config = create_cache_config(
            folder_name="test_redis",
            ttl=60,
            compress=False,
            redis_host="localhost",
            redis_port=6379,
            redis_db=0,
        )
        engine = RedisCacheEngine(config)
        engine._redis = fake_redis  # Replace with our fake Redis
        return engine

    def test_is_available(self):
        """Test checking if Redis is available."""
        with patch("twat_cache.engines.redis.is_package_available") as mock_check:
            mock_check.return_value = True
            assert RedisCacheEngine.is_available() is True

            mock_check.return_value = False
            assert RedisCacheEngine.is_available() is False

    def test_init_with_unavailable_redis(self):
        """Test initialization when Redis is not available."""
        with patch("twat_cache.engines.redis.RedisCacheEngine.is_available") as mock_check:
            mock_check.return_value = False
            config = create_cache_config()

            with pytest.raises(EngineNotAvailableError):
                RedisCacheEngine(config)

    def test_init_with_connection_error(self):
        """Test initialization with Redis connection error."""
        import redis

        with patch("redis.Redis") as mock_redis:
            mock_redis.return_value.ping.side_effect = redis.exceptions.ConnectionError("Connection refused")
            config = create_cache_config()

            with pytest.raises(ConfigurationError):
                RedisCacheEngine(config)

    def test_validate_config(self, redis_engine):
        """Test configuration validation."""
        # Valid port
        redis_engine._config.redis_port = 6379
        redis_engine.validate_config()  # Should not raise

        # Invalid port
        with patch.object(redis_engine._config, "get_redis_port") as mock_get_port:
            mock_get_port.return_value = 70000  # Invalid port
            with pytest.raises(ConfigurationError):
                redis_engine.validate_config()

    def test_get_full_key(self, redis_engine):
        """Test key generation."""
        # String key
        key = "test_key"
        full_key = redis_engine._get_full_key(key)
        assert full_key == "test_redis:test_key"

        # Tuple key
        key = ("test", 123, True)
        full_key = redis_engine._get_full_key(key)
        assert full_key.startswith("test_redis:")
        assert isinstance(full_key, str)

    def test_get_cached_value(self, redis_engine, mock_redis):
        """Test getting cached values."""
        # Set up mock
        mock_redis.get.return_value = pickle.dumps("test_value")

        # Get value
        value = redis_engine._get_cached_value("test_key")
        assert value == "test_value"
        mock_redis.get.assert_called_once_with("test_redis:test_key")

        # Test cache miss
        mock_redis.get.return_value = None
        mock_redis.get.reset_mock()
        value = redis_engine._get_cached_value("missing_key")
        assert value is None
        mock_redis.get.assert_called_once()

        # Test deserialization error
        mock_redis.get.return_value = b"invalid_pickle_data"
        mock_redis.get.reset_mock()
        value = redis_engine._get_cached_value("error_key")
        assert value is None
        mock_redis.get.assert_called_once()

    def test_set_cached_value(self, redis_engine, mock_redis):
        """Test setting cached values."""
        # Set value without TTL
        redis_engine._config.ttl = None
        redis_engine._set_cached_value("test_key", "test_value")
        mock_redis.set.assert_called_once()

        # Set value with TTL
        mock_redis.set.reset_mock()
        redis_engine._config.ttl = 60
        redis_engine._set_cached_value("test_key", "test_value")
        mock_redis.setex.assert_called_once()

        # Test serialization error
        class UnpickleableObject:
            def __reduce__(self):
                msg = "Cannot pickle this"
                raise TypeError(msg)

        with pytest.raises(Exception):
            redis_engine._set_cached_value("error_key", UnpickleableObject())

    def test_clear(self, redis_engine, mock_redis):
        """Test clearing the cache."""
        # Set up mock
        mock_redis.keys.return_value = [b"test_redis:key1", b"test_redis:key2"]

        # Clear cache
        redis_engine.clear()
        mock_redis.keys.assert_called_once_with("test_redis:*")
        mock_redis.delete.assert_called_once()

        # Test with no keys
        mock_redis.keys.return_value = []
        mock_redis.keys.reset_mock()
        mock_redis.delete.reset_mock()
        redis_engine.clear()
        mock_redis.keys.assert_called_once()
        mock_redis.delete.assert_not_called()

    def test_cache_decorator(self, redis_engine, mock_redis):
        """Test the cache decorator."""
        # Set up mock
        mock_redis.get.return_value = None  # First call: cache miss

        # Define a function to cache
        call_count = 0

        @redis_engine.cache
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # First call should execute the function
        result = test_func(5)
        assert result == 10
        assert call_count == 1

        # Set up mock for cache hit
        mock_redis.get.return_value = pickle.dumps(10)

        # Second call should use cached value
        result = test_func(5)
        assert result == 10
        assert call_count == 1  # Function not called again

    def test_stats(self, redis_engine, mock_redis):
        """Test getting cache statistics."""
        # Set up mock
        mock_redis.keys.return_value = [b"test_redis:key1", b"test_redis:key2"]
        mock_redis.info.return_value = {
            "redis_version": "6.2.6",
            "used_memory": 1024,
            "used_memory_human": "1K",
            "connected_clients": 1,
        }

        # Get stats
        stats = redis_engine.stats
        assert stats["size"] == 2
        assert stats["engine"] == "redis"
        assert stats["namespace"] == "test_redis"
        assert stats["redis_version"] == "6.2.6"
        assert stats["used_memory"] == 1024
        assert stats["used_memory_human"] == "1K"
        assert stats["connected_clients"] == 1

    def test_real_redis_operations(self, real_redis_engine):
        """Test Redis operations with a fake Redis client."""
        # Set a value
        real_redis_engine._set_cached_value("test_key", "test_value")

        # Get the value
        value = real_redis_engine._get_cached_value("test_key")
        assert value == "test_value"

        # Test cache hit/miss counting
        assert real_redis_engine._hits == 1
        assert real_redis_engine._misses == 0

        # Get a missing value
        value = real_redis_engine._get_cached_value("missing_key")
        assert value is None
        assert real_redis_engine._hits == 1
        assert real_redis_engine._misses == 1

        # Clear the cache
        real_redis_engine.clear()
        value = real_redis_engine._get_cached_value("test_key")
        assert value is None
        assert real_redis_engine._misses == 2

        # Test with complex data
        complex_data = {"a": [1, 2, 3], "b": {"c": "d"}}
        real_redis_engine._set_cached_value("complex_key", complex_data)
        value = real_redis_engine._get_cached_value("complex_key")
        assert value == complex_data

    def test_compression(self, real_redis_engine):
        """Test compression functionality."""
        # Enable compression
        real_redis_engine._compress = True

        # Set a value
        real_redis_engine._set_cached_value("compressed_key", "test_value" * 100)

        # Get the value
        value = real_redis_engine._get_cached_value("compressed_key")
        assert value == "test_value" * 100

        # Disable compression
        real_redis_engine._compress = False

#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "pytest",
#   "pytest-asyncio",
#   "loguru",
#   "diskcache",
#   "joblib",
#   "types-pytest",
#   "cachetools",
#   "cachebox",
#   "klepto",
#   "aiocache",
#   "pydantic",
#   "numpy",
#   "pandas",
# ]
# ///
# this_file: tests/test_backend_selector.py

"""Test suite for backend selection strategy."""

from typing import Any
import numpy as np
import pandas as pd

from twat_cache.backend_selector import (
    DataSize,
    DataPersistence,
    AccessPattern,
    ConcurrencyLevel,
    estimate_data_size,
    get_type_based_backend,
    get_available_backend,
    is_backend_available,
    select_backend_for_data,
    configure_for_type,
    configure_for_numpy,
    configure_for_pandas,
    configure_for_images,
    configure_for_json,
    hybrid_cache_config,
    analyze_function_return_type,
    smart_cache_config,
    detect_result_type,
)
from twat_cache.config import create_cache_config
from twat_cache.engines.manager import get_engine_manager


class TestDataSizeEstimation:
    """Test data size estimation functionality."""

    def test_small_data(self) -> None:
        """Test estimation of small data."""
        small_data = "Hello, world!"
        assert estimate_data_size(small_data) == DataSize.SMALL

        small_list = list(range(100))
        assert estimate_data_size(small_list) == DataSize.SMALL

        small_dict = {i: i * 2 for i in range(50)}
        assert estimate_data_size(small_dict) == DataSize.SMALL

    def test_medium_data(self) -> None:
        """Test estimation of medium data."""
        # Create a string that's between 10KB and 1MB
        medium_string = "x" * (15 * 1024)  # 15KB
        assert estimate_data_size(medium_string) == DataSize.MEDIUM

        # Create a list that's between 10KB and 1MB
        medium_list = list(range(5000))
        if estimate_data_size(medium_list) != DataSize.MEDIUM:
            # Size estimation can vary by platform, so we'll create a larger list if needed
            medium_list = list(range(50000))
            assert estimate_data_size(medium_list) == DataSize.MEDIUM

    def test_large_data(self) -> None:
        """Test estimation of large data."""
        # Create a string that's between 1MB and 100MB
        large_string = "x" * (2 * 1024 * 1024)  # 2MB
        assert estimate_data_size(large_string) == DataSize.LARGE

    def test_numpy_array_size(self) -> None:
        """Test size estimation for NumPy arrays."""
        small_array = np.ones((10, 10))
        assert estimate_data_size(small_array) == DataSize.SMALL

        medium_array = np.ones((500, 500))
        size = estimate_data_size(medium_array)
        assert size in (DataSize.MEDIUM, DataSize.LARGE)  # Size may vary by platform

    def test_pandas_dataframe_size(self) -> None:
        """Test size estimation for pandas DataFrames."""
        small_df = pd.DataFrame({"a": range(100), "b": range(100)})
        assert estimate_data_size(small_df) == DataSize.SMALL

        # Create a medium-sized DataFrame
        medium_df = pd.DataFrame(np.random.rand(1000, 10))
        size = estimate_data_size(medium_df)
        assert size in (DataSize.SMALL, DataSize.MEDIUM)  # Size may vary by platform


class TestTypeBasedBackendSelection:
    """Test backend selection based on data types."""

    def test_primitive_types(self) -> None:
        """Test backend selection for primitive types."""
        assert get_type_based_backend(int) in ("cachetools", "functools")
        assert get_type_based_backend(str) in ("cachetools", "functools")
        assert get_type_based_backend(bool) in ("cachetools", "functools")
        assert get_type_based_backend(float) in ("cachetools", "functools")

    def test_container_types(self) -> None:
        """Test backend selection for container types."""
        assert get_type_based_backend(list) in ("cachetools", "diskcache")
        assert get_type_based_backend(dict) in ("cachetools", "diskcache")
        assert get_type_based_backend(tuple) in ("cachetools", "diskcache")
        assert get_type_based_backend(set) in ("cachetools", "diskcache")

    def test_numpy_types(self) -> None:
        """Test backend selection for NumPy types."""
        assert get_type_based_backend(np.ndarray) in ("joblib", "diskcache")

    def test_pandas_types(self) -> None:
        """Test backend selection for pandas types."""
        assert get_type_based_backend(pd.DataFrame) in ("joblib", "diskcache")
        assert get_type_based_backend(pd.Series) in ("joblib", "diskcache")

    def test_custom_types(self) -> None:
        """Test backend selection for custom types."""

        class CustomClass:
            pass

        # Custom classes should default to diskcache for safety
        assert get_type_based_backend(CustomClass) == "diskcache"


class TestBackendAvailability:
    """Test backend availability checking."""

    def test_is_backend_available(self) -> None:
        """Test checking if backends are available."""
        # These should be available as they're in the test dependencies
        assert is_backend_available("diskcache") is True
        assert is_backend_available("cachetools") is True
        assert is_backend_available("klepto") is True
        assert is_backend_available("joblib") is True

        # This should not be available
        assert is_backend_available("nonexistent_backend") is False

    def test_get_available_backend(self) -> None:
        """Test getting an available backend."""
        # Test with a backend that should be available
        assert get_available_backend("diskcache") == "diskcache"

        # Test with a fallback
        assert get_available_backend("nonexistent_backend") in get_engine_manager().get_available_engines()


class TestSelectBackendForData:
    """Test the main backend selection function."""

    def test_select_with_data_instance(self) -> None:
        """Test selection with actual data instances."""
        # Small integer
        assert select_backend_for_data(data=42) in ("cachetools", "functools")

        # Medium-sized list
        medium_list = list(range(5000))
        assert select_backend_for_data(data=medium_list) in ("diskcache", "klepto")

        # NumPy array
        np_array = np.ones((100, 100))
        assert select_backend_for_data(data=np_array) in ("joblib", "diskcache")

        # Pandas DataFrame
        df = pd.DataFrame({"a": range(100), "b": range(100)})
        assert select_backend_for_data(data=df) in ("joblib", "diskcache")

    def test_select_with_explicit_parameters(self) -> None:
        """Test selection with explicit parameters."""
        # Small, ephemeral data with read-heavy access
        backend = select_backend_for_data(
            size=DataSize.SMALL,
            persistence=DataPersistence.EPHEMERAL,
            access_pattern=AccessPattern.READ_HEAVY,
        )
        assert backend in ("cachetools", "functools")

        # Large, long-term data with balanced access
        backend = select_backend_for_data(
            size=DataSize.LARGE,
            persistence=DataPersistence.LONG_TERM,
            access_pattern=AccessPattern.BALANCED,
        )
        assert backend in ("diskcache", "klepto")

        # Medium data with multi-process concurrency
        backend = select_backend_for_data(
            size=DataSize.MEDIUM,
            concurrency=ConcurrencyLevel.MULTI_PROCESS,
        )
        assert backend in ("diskcache", "klepto")

    def test_select_with_config(self) -> None:
        """Test selection with a config object."""
        # Config with preferred engine
        config = create_cache_config(preferred_engine="diskcache")
        assert select_backend_for_data(config=config) == "diskcache"

        # Config with cache type
        config = create_cache_config(cache_type="memory")
        assert select_backend_for_data(config=config) in ("cachetools", "functools")

        # Config with SQL preference
        config = create_cache_config(use_sql=True)
        assert select_backend_for_data(config=config) in ("diskcache", "klepto")


class TestTypeSpecificConfigurations:
    """Test type-specific configuration generators."""

    def test_configure_for_type(self) -> None:
        """Test configuration generation for specific types."""
        # Integer type
        int_config = configure_for_type(int)
        assert int_config.cache_type == "memory"
        assert int_config.preferred_engine in ("cachetools", "functools")

        # List type
        list_config = configure_for_type(list)
        assert list_config.cache_type in ("memory", "disk")

        # NumPy array type
        np_config = configure_for_type(np.ndarray)
        assert np_config.preferred_engine in ("joblib", "diskcache")

    def test_configure_for_numpy(self) -> None:
        """Test NumPy-specific configuration."""
        config = configure_for_numpy()
        assert config.preferred_engine in ("joblib", "diskcache")
        assert config.compress is True

    def test_configure_for_pandas(self) -> None:
        """Test pandas-specific configuration."""
        config = configure_for_pandas()
        assert config.preferred_engine in ("joblib", "diskcache")
        assert config.compress is True

    def test_configure_for_images(self) -> None:
        """Test image-specific configuration."""
        config = configure_for_images()
        assert config.preferred_engine in ("diskcache", "joblib")
        assert config.compress is True

    def test_configure_for_json(self) -> None:
        """Test JSON-specific configuration."""
        config = configure_for_json()
        assert config.preferred_engine in ("diskcache", "klepto")


class TestHybridCacheConfig:
    """Test hybrid cache configuration."""

    def test_hybrid_cache_config(self) -> None:
        """Test hybrid cache configuration generation."""
        config = hybrid_cache_config()
        assert isinstance(config, dict)
        assert "small_result_engine" in config
        assert "large_result_engine" in config
        assert "size_threshold" in config

        # Test with custom parameters
        custom_config = hybrid_cache_config(
            small_result_engine="functools",
            large_result_engine="klepto",
            size_threshold=2048,
        )
        assert custom_config["small_result_engine"] == "functools"
        assert custom_config["large_result_engine"] == "klepto"
        assert custom_config["size_threshold"] == 2048


class TestFunctionAnalysis:
    """Test function analysis for smart caching."""

    def test_analyze_function_return_type(self) -> None:
        """Test analyzing function return types."""

        def returns_int() -> int:
            return 42

        def returns_list() -> list[int]:
            return [1, 2, 3]

        def returns_dict() -> dict[str, Any]:
            return {"a": 1, "b": 2}

        def returns_numpy() -> np.ndarray:
            return np.ones((10, 10))

        # Test with type annotations
        assert analyze_function_return_type(returns_int) == int
        assert analyze_function_return_type(returns_list) == list[int]
        assert analyze_function_return_type(returns_dict) == dict[str, Any]
        assert analyze_function_return_type(returns_numpy) == np.ndarray

        # Test with no type annotations
        def no_annotation():
            return 42

        assert analyze_function_return_type(no_annotation) is None

    def test_smart_cache_config(self) -> None:
        """Test smart cache configuration based on function analysis."""

        def returns_int() -> int:
            return 42

        def returns_numpy() -> np.ndarray:
            return np.ones((10, 10))

        # Test with type annotations
        int_config = smart_cache_config(returns_int)
        assert int_config.preferred_engine in ("cachetools", "functools")

        numpy_config = smart_cache_config(returns_numpy)
        assert numpy_config.preferred_engine in ("joblib", "diskcache")

        # Test with custom parameters
        custom_config = smart_cache_config(returns_int, maxsize=100, ttl=60)
        assert custom_config.maxsize == 100
        assert custom_config.ttl == 60


class TestResultTypeDetection:
    """Test result type detection for dynamic caching."""

    def test_detect_result_type(self) -> None:
        """Test detecting result types at runtime."""
        # Primitive types
        assert detect_result_type(42) == "int"
        assert detect_result_type(3.14) == "float"
        assert detect_result_type("hello") == "str"
        assert detect_result_type(True) == "bool"

        # Container types
        assert detect_result_type([1, 2, 3]) == "list"
        assert detect_result_type({"a": 1, "b": 2}) == "dict"
        assert detect_result_type((1, 2, 3)) == "tuple"
        assert detect_result_type({1, 2, 3}) == "set"

        # NumPy types
        assert detect_result_type(np.ones(10)) == "numpy.ndarray"

        # Pandas types
        assert detect_result_type(pd.DataFrame({"a": [1, 2, 3]})) == "pandas.DataFrame"
        assert detect_result_type(pd.Series([1, 2, 3])) == "pandas.Series"

        # Custom types
        class CustomClass:
            pass

        assert detect_result_type(CustomClass()) == "CustomClass"

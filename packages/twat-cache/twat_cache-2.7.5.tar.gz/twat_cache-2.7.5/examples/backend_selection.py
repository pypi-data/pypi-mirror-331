#!/usr/bin/env python3
# this_file: examples/backend_selection.py

"""
Example demonstrating the data type-based backend selection strategy.

This example shows how to use the smart backend selection features
to automatically choose the most appropriate cache backend based on
the characteristics of the data being cached.
"""

import time
from typing import Any

from twat_cache import (
    # Basic decorators
    ucache,
    # Backend selection utilities
    configure_for_numpy,
    configure_for_json,
    hybrid_cache,
    smart_cache,
)


# Example 1: Using type-specific configuration helpers
def example_type_specific_config():
    """Demonstrate type-specific configuration helpers."""
    print("\n=== Example 1: Type-specific Configuration Helpers ===")

    # For NumPy arrays (if numpy is installed)
    try:
        import numpy as np

        @ucache(config=configure_for_numpy())
        def process_array(data: np.ndarray) -> np.ndarray:
            """Process a NumPy array with appropriate caching."""
            print("  Processing NumPy array...")
            time.sleep(1)  # Simulate processing time
            return data * 2

        # Create a sample array
        arr = np.array([1, 2, 3, 4, 5])

        # First call (cache miss)
        print("  First call (cache miss):")
        start = time.time()
        result1 = process_array(arr)
        print(f"  Result: {result1}")
        print(f"  Time: {time.time() - start:.4f} seconds")

        # Second call (cache hit)
        print("\n  Second call (cache hit):")
        start = time.time()
        result2 = process_array(arr)
        print(f"  Result: {result2}")
        print(f"  Time: {time.time() - start:.4f} seconds")

    except ImportError:
        print("  NumPy not installed, skipping NumPy example")

    # For JSON data
    @ucache(config=configure_for_json())
    def fetch_json_data(url: str) -> dict[str, Any]:
        """Fetch JSON data with appropriate caching."""
        print(f"  Fetching JSON data from {url}...")
        time.sleep(1)  # Simulate network request
        return {"data": [1, 2, 3, 4, 5], "metadata": {"source": url}}

    # First call (cache miss)
    print("\n  JSON example:")
    print("  First call (cache miss):")
    start = time.time()
    json_result1 = fetch_json_data("https://example.com/api/data")
    print(f"  Result: {json_result1}")
    print(f"  Time: {time.time() - start:.4f} seconds")

    # Second call (cache hit)
    print("\n  Second call (cache hit):")
    start = time.time()
    json_result2 = fetch_json_data("https://example.com/api/data")
    print(f"  Result: {json_result2}")
    print(f"  Time: {time.time() - start:.4f} seconds")


# Example 2: Using hybrid caching based on result size
def example_hybrid_caching():
    """Demonstrate hybrid caching based on result size."""
    print("\n=== Example 2: Hybrid Caching Based on Result Size ===")

    @hybrid_cache()
    def get_data(size: str) -> dict[str, Any] | list[int]:
        """
        Return different sized data based on the input.

        This function will return either a small dictionary or a large list
        depending on the input, and the hybrid_cache decorator will select
        the appropriate backend based on the size of the result.
        """
        print(f"  Generating {size} data...")
        time.sleep(1)  # Simulate processing time

        if size == "small":
            # Small result, should use in-memory caching
            return {"name": "Small Data", "value": 42}
        else:
            # Large result, should use disk caching
            return list(range(100000))  # Large list

    # Small data example
    print("\n  Small data example:")
    print("  First call (cache miss):")
    start = time.time()
    small_result1 = get_data("small")
    print(f"  Result size: {len(str(small_result1))} bytes")
    print(f"  Time: {time.time() - start:.4f} seconds")

    print("\n  Second call (cache hit):")
    start = time.time()
    small_result2 = get_data("small")
    print(f"  Result size: {len(str(small_result2))} bytes")
    print(f"  Time: {time.time() - start:.4f} seconds")

    # Large data example
    print("\n  Large data example:")
    print("  First call (cache miss):")
    start = time.time()
    large_result1 = get_data("large")
    print(f"  Result size: {len(str(large_result1))} bytes")
    print(f"  Time: {time.time() - start:.4f} seconds")

    print("\n  Second call (cache hit):")
    start = time.time()
    large_result2 = get_data("large")
    print(f"  Result size: {len(str(large_result2))} bytes")
    print(f"  Time: {time.time() - start:.4f} seconds")


# Example 3: Using smart caching with automatic backend selection
def example_smart_caching():
    """Demonstrate smart caching with automatic backend selection."""
    print("\n=== Example 3: Smart Caching with Automatic Backend Selection ===")

    @smart_cache()
    def process_data(data_type: str, size: int) -> Any:
        """
        Process different types of data.

        This function will return different types of data based on the input,
        and the smart_cache decorator will select the appropriate backend
        based on the characteristics of the result.
        """
        print(f"  Processing {data_type} data of size {size}...")
        time.sleep(1)  # Simulate processing time

        if data_type == "dict":
            return {f"key_{i}": f"value_{i}" for i in range(size)}
        elif data_type == "list":
            return list(range(size))
        elif data_type == "str":
            return "x" * size
        else:
            return size

    # Test with different data types and sizes
    data_types = ["dict", "list", "str", "int"]
    sizes = [10, 10000]

    for data_type in data_types:
        for size in sizes:
            print(f"\n  {data_type.capitalize()} data of size {size}:")
            print("  First call (cache miss):")
            start = time.time()
            result1 = process_data(data_type, size)
            result_size = len(str(result1)) if data_type != "int" else 8
            print(f"  Result type: {type(result1).__name__}, size: {result_size} bytes")
            print(f"  Time: {time.time() - start:.4f} seconds")

            print("\n  Second call (cache hit):")
            start = time.time()
            result2 = process_data(data_type, size)
            print(f"  Result type: {type(result2).__name__}, size: {result_size} bytes")
            print(f"  Time: {time.time() - start:.4f} seconds")


if __name__ == "__main__":
    print("Backend Selection Strategy Examples")
    print("==================================")

    example_type_specific_config()
    example_hybrid_caching()
    example_smart_caching()

    print("\nAll examples completed successfully!")

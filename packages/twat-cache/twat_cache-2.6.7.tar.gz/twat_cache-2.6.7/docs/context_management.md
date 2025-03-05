# Cache Context Management

The `twat_cache` library provides powerful context management utilities that allow you to control the lifecycle of cache engines and ensure proper resource cleanup. This document explains how to use these context management features effectively.

## Overview

Cache context management in `twat_cache` serves several important purposes:

1. **Resource Management**: Ensures that cache resources (files, connections, memory) are properly cleaned up when no longer needed
2. **Temporary Configuration**: Allows you to temporarily override cache settings for specific code blocks
3. **Engine Selection**: Provides a way to explicitly select a specific cache engine for a block of code
4. **Error Handling**: Guarantees cleanup even when exceptions occur

## Available Context Managers

### `engine_context`

The `engine_context` function is a context manager that creates and manages a cache engine instance:

```python
from twat_cache.context import engine_context

# Basic usage
with engine_context() as cache:
    # Use the cache engine
    cache.set("key", "value")
    value = cache.get("key")

# With specific configuration
with engine_context(maxsize=100, folder_name="my_cache") as cache:
    # Use the cache engine with custom configuration
    cache.set("key", "value")

# With specific engine
with engine_context(engine_name="redis") as cache:
    # Use the Redis cache engine
    cache.set("key", "value")
```

### `CacheContext` Class

The `CacheContext` class provides a reusable context manager for working with cache engines:

```python
from twat_cache.context import CacheContext
from twat_cache.config import create_cache_config

# Create a context with default settings
context = CacheContext()
with context as cache:
    # Use the cache engine
    cache.set("key", "value")

# Create a context with specific configuration
config = create_cache_config(maxsize=100, folder_name="my_cache")
context = CacheContext(config=config)
with context as cache:
    # Use the cache engine with custom configuration
    cache.set("key", "value")

# Create a context with a specific engine
redis_context = CacheContext(engine_name="redis")
with redis_context as cache:
    # Use the Redis cache engine
    cache.set("key", "value")
```

## Manual Engine Creation

If you need more control over the engine lifecycle, you can use the `get_or_create_engine` function:

```python
from twat_cache.context import get_or_create_engine

# Create an engine
engine = get_or_create_engine(maxsize=100, folder_name="my_cache")

try:
    # Use the engine
    engine.set("key", "value")
    value = engine.get("key")
finally:
    # Important: You must manually clean up the engine
    engine.cleanup()
```

> **Warning**: When using `get_or_create_engine`, you are responsible for calling `cleanup()` on the engine when it's no longer needed. For automatic cleanup, use `engine_context` or `CacheContext` instead.

## Practical Examples

### Temporary Cache Configuration

```python
from twat_cache.context import engine_context
from twat_cache.decorators import ucache

# Default cache configuration
@ucache()
def slow_function(x):
    # ... expensive computation ...
    return result

# Override cache configuration for a specific section
with engine_context(maxsize=1000, ttl=3600) as cache:
    # Use the cache directly
    key = f"special_key_{x}"
    result = cache.get(key)
    if result is None:
        result = compute_expensive_result(x)
        cache.set(key, result)
```

### Using Different Cache Backends

```python
from twat_cache.context import engine_context

# Process small data with in-memory cache
with engine_context(engine_name="cachetools") as memory_cache:
    for item in small_data:
        process_with_cache(item, memory_cache)

# Process large data with disk cache
with engine_context(engine_name="diskcache") as disk_cache:
    for item in large_data:
        process_with_cache(item, disk_cache)
```

### Redis Cache for Distributed Applications

```python
from twat_cache.context import engine_context

# Use Redis for distributed caching
with engine_context(
    engine_name="redis",
    redis_host="redis.example.com",
    redis_port=6379,
    redis_password="secret",
    ttl=3600,
) as redis_cache:
    # Cache is now shared across all application instances
    result = redis_cache.get("shared_key")
    if result is None:
        result = compute_expensive_result()
        redis_cache.set("shared_key", result)
```

## Best Practices

1. **Use Context Managers**: Always use context managers (`with` statements) when possible to ensure proper resource cleanup.

2. **Specify Engine Requirements**: When you need specific features, explicitly specify the engine name or configuration parameters that provide those features.

3. **Handle Exceptions**: Context managers will clean up resources even when exceptions occur, but you should still handle exceptions appropriately for your application logic.

4. **Reuse Contexts**: For repeated operations with the same configuration, create a `CacheContext` instance once and reuse it.

5. **Avoid Nesting**: While it's technically possible to nest context managers, it can lead to confusion. Try to keep your cache context structure simple.

## Advanced Usage

### Custom Engine Selection Logic

```python
from twat_cache.context import engine_context
from twat_cache.engines.manager import get_engine_manager

# Get available engines
manager = get_engine_manager()
available_engines = manager.get_available_engines()

# Choose an engine based on custom logic
if "redis" in available_engines and is_distributed_environment():
    engine_name = "redis"
elif "diskcache" in available_engines and data_size > 1_000_000:
    engine_name = "diskcache"
else:
    engine_name = "cachetools"

# Use the selected engine
with engine_context(engine_name=engine_name) as cache:
    # Use the cache
    cache.set("key", "value")
```

### Combining with Decorators

```python
from twat_cache.context import engine_context
from twat_cache.decorators import ucache
from functools import wraps

def with_custom_cache(func):
    """Decorator that uses a custom cache configuration."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        with engine_context(maxsize=1000, ttl=3600) as cache:
            # Create a cache key
            key = f"{func.__name__}:{args}:{kwargs}"
            
            # Check cache
            result = cache.get(key)
            if result is not None:
                return result
                
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result
    return wrapper

# Use the custom cache decorator
@with_custom_cache
def expensive_function(x, y):
    # ... expensive computation ...
    return result
```

## Error Handling

The context managers in `twat_cache` are designed to handle errors gracefully:

```python
from twat_cache.context import engine_context
from twat_cache.exceptions import CacheOperationError

try:
    with engine_context() as cache:
        # This might raise an exception
        cache.set("key", complex_object)
        result = cache.get("key")
except CacheOperationError as e:
    # Handle cache-specific errors
    print(f"Cache operation failed: {e}")
except Exception as e:
    # Handle other errors
    print(f"An error occurred: {e}")
finally:
    # The cache engine will be cleaned up automatically
    # No need to call cache.cleanup() here
    print("Cache resources have been cleaned up")
```

## Conclusion

Cache context management in `twat_cache` provides a flexible and robust way to work with cache engines while ensuring proper resource management. By using these context management utilities, you can write cleaner, more maintainable code that efficiently handles cache resources. 
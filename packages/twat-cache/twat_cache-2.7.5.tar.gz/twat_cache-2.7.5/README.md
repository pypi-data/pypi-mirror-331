# twat-cache

A flexible caching utility package for Python functions that provides a unified interface for caching function results using various high-performance backends.

## Features

- Simple decorator interface for caching function results
- Multiple caching backends with automatic selection:
  1. `cachebox` - Very fast Rust-based cache (optional)
  2. `cachetools` - Flexible in-memory caching (optional)
  3. `aiocache` - Async-capable caching (optional)
  4. `klepto` - Scientific computing caching (optional)
  5. `diskcache` - SQL-based disk cache (optional)
  6. `joblib` - Efficient array caching (optional)
  7. `redis` - Distributed caching with Redis (optional)
  8. Memory-based LRU cache (always available)
- Automatic cache directory management
- Type hints and modern Python features
- Lazy backend loading - only imports what you use
- Automatic backend selection based on availability and use case
- Smart backend selection based on data characteristics
- TTL support for cache expiration
- Multiple eviction policies (LRU, LFU, FIFO, RR)
- Async function support
- Compression options for large data
- Secure file permissions for sensitive data
- Hybrid caching with automatic backend switching
- Context management for cache engines
- Comprehensive test suite for all components

## Recent Updates (v2.3.0)

### Enhanced Context Management

The context management system has been significantly improved:
- Better error handling and resource cleanup
- Support for explicit engine selection
- Simplified API for temporary cache configurations
- Automatic cleanup of resources even when exceptions occur

```python
# Example of improved context management
from twat_cache import CacheContext

# Create a context with explicit engine selection
with CacheContext(engine_name="redis", namespace="user_data") as cache:
    # Use the cache within the context
    cache.set("user:1001", {"name": "John", "role": "admin"})
    user = cache.get("user:1001")
    
    # Resources are automatically cleaned up when exiting the context
```

### Refined Backend Selection

The backend selection strategy has been further enhanced:
- More accurate data type detection for optimal backend selection
- Improved fallback mechanisms when preferred backends are unavailable
- Better handling of edge cases for various data types
- Enhanced performance for frequently accessed items

### Comprehensive Documentation

Documentation has been expanded with:
- Detailed examples for all cache backends
- Step-by-step guides for common use cases
- API reference with complete parameter descriptions
- Best practices for cache configuration

## Installation

Basic installation with just LRU caching:
```bash
pip install twat-cache
```

With all optional backends:
```bash
pip install twat-cache[all]
```

Or install specific backends:
```bash
pip install twat-cache[cachebox]     # For Rust-based high-performance cache
pip install twat-cache[cachetools]   # For flexible in-memory caching
pip install twat-cache[aiocache]     # For async-capable caching
pip install twat-cache[klepto]       # For scientific computing caching
pip install twat-cache[diskcache]    # For SQL-based disk caching
pip install twat-cache[joblib]       # For efficient array caching
pip install twat-cache[redis]        # For distributed caching with Redis
```

## Usage

### Basic Memory Caching

For simple in-memory caching with LRU eviction:

```python
from twat_cache import mcache

@mcache(maxsize=100)  # Cache up to 100 items
def expensive_function(x: int) -> int:
    # Expensive computation here
    return x * x

# First call computes
result1 = expensive_function(5)  # Computes 25

# Second call uses cache
result2 = expensive_function(5)  # Returns cached 25
```

### Disk-Based Caching

For persistent caching using SQLite:

```python
from twat_cache import bcache

@bcache(
    folder_name="my_cache",  # Cache directory name
    maxsize=1_000_000,       # Max cache size in bytes
    ttl=3600,               # Cache entries expire after 1 hour
    use_sql=True,           # Use SQLite backend
    secure=True,            # Use secure file permissions
)
def expensive_function(x: int) -> int:
    return x * x
```

### Redis Distributed Caching

For distributed caching with Redis:

```python
from twat_cache import ucache

@ucache(
    preferred_engine="redis",
    folder_name="redis_cache",  # Used as Redis namespace
    ttl=3600,                  # Cache entries expire after 1 hour
    compress=True,             # Enable compression
)
def expensive_function(x: int) -> int:
    return x * x
```

### File-Based Caching

For efficient caching of large objects like NumPy arrays:

```python
from twat_cache import fcache
import numpy as np

@fcache(
    folder_name="array_cache",
    compress=True,           # Enable compression
    secure=True,            # Use secure file permissions
)
def process_array(data: np.ndarray) -> np.ndarray:
    # Expensive array processing here
    return data * 2
```

### Async Caching

For async functions with Redis or memory backend:

```python
from twat_cache import ucache

@ucache(use_async=True)
async def fetch_data(url: str) -> dict:
    # Async web request here
    return {"data": "..."}

# First call fetches
data1 = await fetch_data("https://api.example.com")

# Second call uses cache
data2 = await fetch_data("https://api.example.com")
```

### Universal Caching

Let the library choose the best backend:

```python
from twat_cache import ucache

@ucache(
    folder_name="cache",     # Optional - uses disk cache if provided
    maxsize=1000,           # Optional - limits cache size
    ttl=3600,              # Optional - entries expire after 1 hour
    policy="lru",          # Optional - LRU eviction (default)
    use_sql=True,          # Optional - use SQL backend if available
    compress=True,         # Optional - enable compression
    secure=True,           # Optional - secure file permissions
)
def my_function(x: int) -> int:
    return x * x
```

### Smart Backend Selection

Automatically select the best backend based on data characteristics:

```python
from twat_cache import smart_cache

@smart_cache()
def process_data(data_type: str, size: int) -> Any:
    """Process different types of data with automatic backend selection."""
    if data_type == "dict":
        return {f"key_{i}": f"value_{i}" for i in range(size)}
    elif data_type == "list":
        return [i for i in range(size)]
    elif data_type == "str":
        return "x" * size
    else:
        return size
```

### Hybrid Caching

Switch backends based on result size:

```python
from twat_cache import hybrid_cache

@hybrid_cache()
def get_data(size: str) -> Union[Dict[str, Any], List[int]]:
    """Return different sized data with appropriate backend selection."""
    if size == "small":
        # Small result, will use in-memory caching
        return {"name": "Small Data", "value": 42}
    else:
        # Large result, will use disk caching
        return [i for i in range(100000)]
```

### Type-Specific Configuration

Configure caching based on data types:

```python
from twat_cache import ucache, configure_for_numpy, configure_for_json

# For NumPy arrays
@ucache(config=configure_for_numpy())
def process_array(data: np.ndarray) -> np.ndarray:
    return data * 2

# For JSON data
@ucache(config=configure_for_json())
def fetch_json_data(url: str) -> Dict[str, Any]:
    return {"data": [1, 2, 3, 4, 5], "metadata": {"source": url}}
```

### Cache Management

Clear caches and get statistics:

```python
from twat_cache import clear_cache, get_stats

# Clear all caches
clear_cache()

# Get cache statistics
stats = get_stats()
print(stats)  # Shows hits, misses, size, etc.
```

### Context Management

Use cache engines with context management:

```python
from twat_cache import CacheContext, engine_context

# Method 1: Using the CacheContext class
with CacheContext(engine_name="diskcache", folder_name="cache") as cache:
    # Use the cache
    cache.set("key", "value")
    value = cache.get("key")
    
# Method 2: Using the engine_context function
with engine_context(engine_name="redis", ttl=3600) as cache:
    # Use the cache
    cache.set("key", "value")
    value = cache.get("key")
    
# Cache is automatically closed when exiting the context
```

## Advanced Features

### TTL Support

Set time-to-live for cache entries:

```python
from twat_cache import ucache

@ucache(ttl=3600)  # Entries expire after 1 hour
def get_weather(city: str) -> dict:
    # Fetch weather data
    return {"temp": 20}
```

### Eviction Policies

Choose from different cache eviction policies:

```python
from twat_cache import ucache

# Least Recently Used (default)
@ucache(policy="lru")
def function1(x: int) -> int:
    return x * x

# Least Frequently Used
@ucache(policy="lfu")
def function2(x: int) -> int:
    return x * x

# First In, First Out
@ucache(policy="fifo")
def function3(x: int) -> int:
    return x * x
```

## Documentation

For more detailed documentation, see the following resources:

- [Context Management](docs/context_management.md)
- [Backend Selection](docs/backend_selection.md)
- [Cache Engines](docs/cache_engines.md)
- [Configuration Options](docs/configuration.md)
- [API Reference](docs/api_reference.md)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Rationale

Python provides several powerful caching libraries to help optimize application performance by storing and reusing expensive function results. Let's take an in-depth look at some of the most popular options, comparing their features, backends, methods, and use cases.


### Built-in functools 

Python's standard library offers basic caching functionality through the `functools` module. It provides decorators like `@lru_cache(maxsize, typed)` for simple memoization with a Least Recently Used (LRU) eviction policy. The `@cache` decorator is also available, which is equivalent to an unbounded LRU cache.

- **Backend**: In-memory Python dictionary 
- **Eviction Policy**: LRU or unbounded
- **Concurrency**: Thread-safe via internal locks, but not safe for multi-process use
- **Persistence**: No persistence, cache only exists in memory for the lifetime of the process
- **Best For**: Fast and easy caching of function results in memory with minimal setup

```pyi
### functools.pyi (Partial - Caching related parts)

import typing

_T = typing.TypeVar("_T")

@typing.overload
def lru_cache(maxsize: int | None) -> typing.Callable[[_F], _F]: ...
@typing.overload
def lru_cache(maxsize: int | None, typed: bool) -> typing.Callable[[_F], _F]: ...

class _lru_cache_wrapper(typing.Generic[_F]):
    cache: typing.Dict[typing.Tuple[typing.Any, ...], typing.Any]
    def cache_info(self) -> CacheInfo: ...
    def cache_clear(self) -> None: ...
```

```python
import functools

@functools.lru_cache(maxsize=128)
def expensive_function(x):
    return x * 2
```

### cachetools

The `cachetools` library extends the capabilities of `functools` by offering additional cache classes with various eviction policies like LFU, FIFO, TTL, and RR. It also provides `@cached` and `@cachedmethod` decorators for caching functions and methods.

- **Backend**: In-memory Python dictionary
- **Eviction Policies**: LRU, LFU, TTL, FIFO, RR, TLRU 
- **Concurrency**: Thread-safe, not designed for multi-process use
- **Persistence**: In-memory only, no persistence 
- **Customization**: Configurable `maxsize`, `ttl`, custom `getsizeof` to determine item size
- **Best For**: In-memory caching with specific eviction behavior, e.g. caching web API responses

```pyi
### cachetools.pyi (Partial - Most important classes and decorators)

import typing
from typing import Callable

KT = typing.TypeVar("KT")
VT = typing.TypeVar("VT")
DT = typing.TypeVar("DT")

class Cache(typing.MutableMapping[KT, VT]):
    def __init__(self, maxsize: int, getsizeof: Callable[[VT], int] | None = ...) -> None: ...
    @property
    def maxsize(self) -> int: ...
    @property
    def currsize(self) -> int: ...
    def get(self, key: KT, default: DT = ...) -> VT | DT: ...
    def pop(self, key: KT, default: DT = ...) -> VT | DT: ...
    def setdefault(self, key: KT, default: DT = ...) -> VT | DT: ...
    def clear(self) -> None: ...
    @staticmethod
    def getsizeof(value: Any) -> int: ...

class LRUCache(Cache[KT, VT]):
    def __init__(self, maxsize: int, getsizeof: Callable[[VT], int] | None = ...) -> None: ...
    def popitem(self) -> tuple[KT, VT]: ...

class LFUCache(Cache[KT, VT]):
    def __init__(self, maxsize: int, getsizeof: Callable[[VT], int] | None = ...) -> None: ...
    def popitem(self) -> tuple[KT, VT]: ...

class TTLCache(LRUCache[KT, VT]):
    def __init__(self, maxsize: int, ttl: int, timer: Callable[[], float] | None = ..., getsizeof: Callable[[VT], int] | None = ...) -> None: ...
    @property
    def ttl(self) -> int: ...
    def expire(self, time: float | None = ...) -> list[tuple[KT, VT]]: ...
    def popitem(self) -> tuple[KT, VT]: ...

class _CacheInfo(NamedTuple):
    hits: int
    misses: int
    maxsize: int
    currsize: int

_KeyFunc = Callable[..., typing.Hashable]
_Cache = TypeVar("_Cache", bound=Cache)

@overload
def cached(
    cache: _Cache,
    key: _KeyFunc = ...,
    lock: Any | None = ...,
    info: Literal[False] = ...,
) -> Callable[[_F], _F]: ...
@overload
def cached(
    cache: _Cache,
    key: _KeyFunc = ...,
    lock: Any | None = ...,
    info: Literal[True] = ...,
) -> Callable[[_F], _F]: ...

@overload
def cachedmethod(
    cache: Callable[[Any], _Cache],
    key: _KeyFunc = ...,
    lock: Callable[[Any], Any] | None = ...,
) -> Callable[[_F], _F]: ...
@overload
def cachedmethod(
    cache: Callable[[Any], _Cache],
    key: _KeyFunc = ...,
    lock: None = ...,
) -> Callable[[_F], _F]: ...
```

### cachebox

`cachebox` is an in-memory caching solution accelerated by a Rust backend for enhanced performance. It supports similar eviction policies as `cachetools` including a unique variable TTL cache.

- **Backend**: Rust-backed in-memory store
- **Eviction Policies**: LRU, LFU, FIFO, TTL, RR, variable TTL
- **Concurrency**: Thread-safe Rust implementation, but in-memory only
- **Decorators**: `@cached`, `@cachedmethod` support custom key generation and callbacks
- **Best For**: Performant in-memory caching with ample policy choices

```pyi
### cachebox.pyi (Partial - Most important classes)

import typing

KT = typing.TypeVar("KT")
VT = typing.TypeVar("VT")
DT = typing.TypeVar("DT")


class BaseCacheImpl(Generic[KT, VT]):

    def __init__(
        self,
        maxsize: int,
        iterable: Union[Iterable[Tuple[KT, VT]], Dict[KT, VT]] = ...,
        *,
        capacity: int = ...,
    ) -> None: ...
    @property
    def maxsize(self) -> int: ...
    def __len__(self) -> int: ...
    def __contains__(self, key: KT) -> bool: ...
    def __setitem__(self, key: KT, value: VT) -> None: ...
    def __getitem__(self, key: KT) -> VT: ...
    def __delitem__(self, key: KT) -> VT: ...
    def __iter__(self) -> typing.Iterator[KT]: ...
    def capacity(self) -> int: ...
    def is_full(self) -> bool: ...
    def is_empty(self) -> bool: ...
    def insert(self, key: KT, value: VT) -> typing.Optional[VT]: ...
    def get(self, key: KT, default: DT = None) -> typing.Union[VT, DT]: ...
    def pop(self, key: KT, default: DT = None) -> typing.Union[VT, DT]: ...
    def setdefault(
        self, key: KT, default: typing.Optional[DT] = None
    ) -> typing.Optional[VT | DT]: ...
    def popitem(self) -> typing.Tuple[KT, VT]: ...
    def drain(self, n: int) -> int: ...
    def clear(self, *, reuse: bool = False) -> None: ...
    def shrink_to_fit(self) -> None: ...
    def update(
        self, iterable: typing.Union[typing.Iterable[typing.Tuple[KT, VT]], typing.Dict[KT, VT]]
    ) -> None: ...
    def keys(self) -> typing.Iterable[KT]: ...
    def values(self) -> typing.Iterable[VT]: ...
    def items(self) -> typing.Iterable[typing.Tuple[KT, VT]]: ...

class Cache(BaseCacheImpl[KT, VT]):
    def __init__(
        self,
        maxsize: int,
        iterable: Union[Iterable[Tuple[KT, VT]], Dict[KT, VT]] = ...,
        *,
        capacity: int = ...,
    ) -> None:
        ...
    def popitem(self) -> typing.NoReturn: ...  # not implemented for this class
    def drain(self, n: int) -> typing.NoReturn: ...  # not implemented for this class


class FIFOCache(BaseCacheImpl[KT, VT]):
    def __init__(
        self,
        maxsize: int,
        iterable: Union[Iterable[Tuple[KT, VT]], Dict[KT, VT]] = ...,
        *,
        capacity: int = ...,
    ) -> None:
        ...

class RRCache(BaseCacheImpl[KT, VT]):
    def __init__(
        self,
        maxsize: int,
        iterable: Union[Iterable[Tuple[KT, VT]], Dict[KT, VT]] = ...,
        *,
        capacity: int = ...,
    ) -> None:
        ...

class TTLCache(BaseCacheImpl[KT, VT]):
    def __init__(
        self,
        maxsize: int,
        ttl: float,
        iterable: Union[Iterable[Tuple[KT, VT]], Dict[KT, VT]] = ...,
        *,
        capacity: int = ...,
    ) -> None:
        ...

class LRUCache(BaseCacheImpl[KT, VT]):
    def __init__(
        self,
        maxsize: int,
        iterable: Union[Iterable[Tuple[KT, VT]], Dict[KT, VT]] = ...,
        *,
        capacity: int = ...,
    ) -> None:
        ...

class LFUCache(BaseCacheImpl[KT, VT]):
    def __init__(
        self,
        maxsize: int,
        iterable: Union[Iterable[Tuple[KT, VT]], Dict[KT, VT]] = ...,
        *,
        capacity: int = ...,
    ) -> None:
        ...

class VTTLCache(BaseCacheImpl[KT, VT]):
    def __init__(
        self,
        maxsize: int,
        iterable: Union[Iterable[Tuple[KT, VT]], Dict[KT, VT]] = ...,
        ttl: Optional[float] = 0.0,
        *,
        capacity: int = ...,
    ) -> None:
        ...

_CacheType = TypeVar("_CacheType", bound=BaseCacheImpl)

def cached(cache: typing.Optional[_CacheType], key_maker: typing.Optional[Callable[[tuple, dict], typing.Hashable]] = ..., clear_reuse: bool = ..., callback: typing.Optional[Callable[[int, typing.Any, typing.Any], typing.Any]] = ..., copy_level: int = ..., always_copy: typing.Optional[bool] = ...) -> Callable[[_F], _F]: ...
def cachedmethod(cache: typing.Optional[_CacheType], key_maker: typing.Optional[Callable[[tuple, dict], typing.Hashable]] = ..., clear_reuse: bool = ..., callback: typing.Optional[Callable[[int, typing.Any, typing.Any], typing.Any]] = ..., copy_level: int = ..., always_copy: typing.Optional[bool] = ...) -> Callable[[_F], _F]: ...
```

### klepto

For advanced caching workflows, `klepto` provides a highly flexible solution supporting both in-memory and persistent backends like file archives, SQL databases, and HDF5 files. It allows customizing how cache keys are generated and extends the standard cache eviction policies.

- **Backends**: In-memory dict, file archives, SQL databases, HDF5 files
- **Eviction Policies**: Same as `functools` plus LFU, MRU, RR
- **Key Mapping**: `hashmap`, `stringmap`, `picklemap` algorithms to generate keys
- **Persistence**: Archives cache to disk or database for long-term storage
- **Concurrency**: Locking for thread-safety, some process-safety depending on backend
- **Best For**: Complex scenarios needing transient and persistent caching

```pyi
### key maps
class keymap:
    def __init__(self, typed: bool = False, flat: bool = True,
                 sentinel: object=...) -> None: ...
    def __call__(self, *args, **kwargs) -> object: ...

class hashmap(keymap):
    def __init__(self, algorithm: Optional[str] = None,
                 typed: bool = False, flat: bool = True,
                 sentinel: object=...) -> None: ...

class stringmap(keymap):
    def __init__(self, encoding: Optional[str] = None,
                 typed: bool = False, flat: bool = True,
                 sentinel: object=...) -> None: ...

class picklemap(keymap):
    def __init__(self, serializer: Optional[str] = None,
                 typed: bool = False, flat: bool = True,
                 sentinel: object=...) -> None: ...

### base archive
class archive(dict):
    def __init__(self, *args, **kwds) -> None: ...
    def __asdict__(self) -> dict: ...
    def __repr__(self) -> str: ...
    def copy(self, name: Optional[str] = None) -> 'archive': ...
    def load(self, *args) -> None: ...
    def dump(self, *args) -> None: ...
    def archived(self, *on) -> bool: ...
    def sync(self, clear: bool = False) -> None: ...
    def drop(self) -> None: ...
    def open(self, archive: 'archive') -> None: ...

    @property
    def archive(self) -> 'archive': ...
    @archive.setter
    def archive(self, archive: 'archive') -> None: ...
    @property
    def name(self) -> str: ...
    @name.setter
    def name(self, archive: 'archive') -> None: ...
    @property
    def state(self) -> dict: ...
    @state.setter
    def state(self, archive: 'archive') -> None: ...

class dict_archive(archive):
    def __init__(self, *args, **kwds) -> None: ...

class null_archive(archive):
    def __init__(self, *args, **kwds) -> None: ...

class file_archive(archive):
    def __init__(self, filename: Optional[str] = None, dict: Optional[dict] = None,
                 cached: bool = True, serialized: bool = True,
                 protocol: Optional[int] = None, *args, **kwds) -> None: ...

class dir_archive(archive):
    def __init__(self, dirname: Optional[str] = None, dict: Optional[dict] = None,
                 cached: bool = True, serialized: bool = True,
                 compression: int = 0, permissions: Optional[int] = None,
                 memmode: Optional[str] = None, memsize: int = 100,
                 protocol: Optional[int] = None, *args, **kwds) -> None: ...

class sqltable_archive(archive):
    def __init__(self, database: Optional[str] = None,
                 table: Optional[str] = None, dict: Optional[dict] = None,
                 cached: bool = True, serialized: bool = True,
                 protocol: Optional[int] = None, *args, **kwds) -> None: ...

class sql_archive(archive):
    def __init__(self, database: Optional[str] = None, dict: Optional[dict] = None,
                 cached: bool = True, serialized: bool = True,
                 protocol: Optional[int] = None, *args, **kwds) -> None: ...

class hdfdir_archive(archive):
    def __init__(self, dirname: Optional[str] = None, dict: Optional[dict] = None,
                 cached: bool = True, serialized: bool = True,
                 permissions: Optional[int] = None,
                 protocol: Optional[int] = None, *args, **kwds) -> None: ...

class hdf_archive(archive):
    def __init__(self, filename: Optional[str] = None, dict: Optional[dict] = None,
                 cached: bool = True, serialized: bool = True,
                 protocol: Optional[int] = None, *args, **kwds) -> None: ...
```

### diskcache

When caching large datasets that should survive process restarts, `diskcache` shines with its optimized disk-backed storage using SQLite and the filesystem. It offers a range of eviction policies, a sharded `FanoutCache`, and persistent data structures like `Deque` and `Index`.

- **Backend**: SQLite for metadata, filesystem for data
- **Eviction Policies**: Configurable, including LRU and LFU
- **Persistence**: Data persists on disk between process runs
- **Concurrency**: Thread and process-safe 
- **Added Features**: Stampede prevention, throttling, optimized I/O
- **Best For**: Persistent caching for web apps and data pipelines

```pyi
### diskcache.pyi (Partial - Most important classes)

import typing
from typing import Callable, List, Dict, Any, IO, Optional, Tuple, Union

class Cache:
    def __init__(self, directory: Optional[str] = ..., timeout: float = ..., disk: Type[Disk] = ..., **settings: Any) -> None: ...
    @property
    def directory(self) -> str: ...
    @property
    def timeout(self) -> float: ...
    @property
    def disk(self) -> Disk: ...
    def set(self, key: Any, value: Any, expire: Optional[float] = ..., read: bool = ..., tag: Optional[str] = ..., retry: bool = ...) -> bool: ...
    def get(self, key: Any, default: Optional[Any] = ..., read: bool = ..., expire_time: bool = ..., tag: bool = ..., retry: bool = ...) -> Any: ...
    def delete(self, key: Any, retry: bool = ...) -> bool: ...
    def clear(self, retry: bool = ...) -> int: ...
    def volume(self) -> int: ...
    def check(self, fix: bool = ..., retry: bool = ...) -> List[warnings.WarningMessage]: ...
    def transact(self, retry: bool = ...) -> ContextManager[Callable]: ...
    def memoize(self, name: Optional[str] = ..., typed: bool = ..., expire: Optional[float] = ..., tag: Optional[str] = ..., ignore: typing.Iterable[str] = ...) -> Callable[[_F], _F]: ...
    def close(self) -> None: ...
    def volume(self) -> int: ...
    def stats(self, enable: bool = ..., reset: bool = ...) -> Tuple[int, int]: ...
    def volume(self) -> int: ...

class FanoutCache:
    def __init__(self, directory: Optional[str] = ..., shards: int = ..., timeout: float = ..., disk: Type[Disk] = ..., **settings: Any) -> None: ...
    @property
    def directory(self) -> str: ...
    def transact(self, retry: bool = ...) -> ContextManager[Callable]: ...
    def set(self, key: Any, value: Any, expire: Optional[float] = ..., read: bool = ..., tag: Optional[str] = ..., retry: bool = ...) -> bool: ...
    def get(self, key: Any, default: Optional[Any] = ..., read: bool = ..., expire_time: bool = ..., tag: bool = ..., retry: bool = ...) -> Any: ...
    def delete(self, key: Any, retry: bool = ...) -> bool: ...
    def clear(self, retry: bool = ...) -> int: ...
    def volume(self) -> int: ...
    def stats(self, enable: bool = ..., reset: bool = ...) -> Tuple[int, int]: ...
    def memoize(self, name: Optional[str] = ..., typed: bool = ..., expire: Optional[float] = ..., tag: Optional[str] = ..., ignore: typing.Iterable[str] = ...) -> Callable[[_F], _F]: ...
    def close(self) -> None: ...
    def volume(self) -> int: ...

class Disk:
    def __init__(self, directory: str, min_file_size: int = ..., pickle_protocol: int = ...) -> None: ...
    @property
    def min_file_size(self) -> int: ...
    @property
    def pickle_protocol(self) -> int: ...
    def put(self, key: Any) -> Tuple[Union[str, sqlite3.Binary, int, float], bool]: ...
    def get(self, key: Union[str, sqlite3.Binary, int, float], raw: bool) -> Any: ...
    def store(self, value: Any, read: bool, key: Constant = ...) -> Tuple[int, int, Optional[str], Optional[Union[str, sqlite3.Binary, int, float]]]: ...
    def fetch(self, mode: int, filename: Optional[str], value: Optional[Union[str, sqlite3.Binary, int, float]], read: bool) -> Any: ...

class JSONDisk(Disk):
    def __init__(self, directory: str, compress_level: int = ..., **kwargs: Any) -> None: ...
```

### joblib

Designed for scientific computing and ML workflows, `joblib` offers transparent disk-caching for functions, with optimizations for large NumPy arrays. Results are saved to disk and only re-computed when inputs change.

- **Backend**: Filesystem
- **Persistence**: Caches results to disk for costly computations
- **Memoization**: `@memory.cache` decorator for functions
- **Serialization**: Pickle-based with optional compression
- **Concurrency**: Process-safe file locking
- **Best For**: Caching ML models, features, large NumPy arrays

```pyi
### joblib.pyi (Partial - Most important classes and functions)

import typing
from typing import Callable, List, Dict, Any, IO, Optional, Tuple, Union

_F = TypeVar("_F", bound=Callable[..., Any])

class Memory:
    def __init__(self, location: Optional[str] = ..., backend: str = ..., verbose: int = ..., bytes_limit: Optional[Union[int, str]] = ..., mmap_mode: Optional[str] = ..., compress: Union[bool, int] = ..., backend_options: Optional[Dict[str, Any]] = ...) -> None: ...
    @property
    def location(self) -> str: ...
    @property
    def backend(self) -> str: ...
    @property
    def compress(self) -> Union[bool, int]: ...
    @property
    def verbose(self) -> int: ...
    def cache(self, func: Optional[_F] = ..., ignore: Optional[List[str]] = ..., verbose: Optional[int] = ..., mmap_mode: Optional[str] = ..., cache_validation_callback: Optional[Callable[[Dict[str, Any]], bool]] = ...) -> _F: ...
    def clear(self, warn: bool = ...) -> None: ...
    def eval(self, func: _F, *args: Any, **kwargs: Any) -> Any: ...
    def __call__(self, func: _F, *args: Any, **kwargs: Any) -> Any: ...

class Parallel:
    def __init__(self, n_jobs: Optional[int] = ..., backend: Optional[str] = ..., verbose: int = ..., timeout: Optional[float] = ..., pre_dispatch: Union[str, int] = ..., batch_size: Union[str, int] = ..., temp_folder: Optional[str] = ..., max_nbytes: Optional[Union[int, str]] = ..., mmap_mode: Optional[str] = ..., prefer: Optional[str] = ..., require: Optional[str] = ...) -> None: ...
    def __call__(self, iterable: typing.Iterable) -> List[Any]: ...
    def __enter__(self) -> "Parallel": ...
    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_value: Optional[BaseException], traceback: Optional[TracebackType]) -> None: ...
    def submit(self, func: _F, *args: Any, **kwargs: Any) -> concurrent.futures.Future: ...
    def map(self, func: _F, *iterables: typing.Iterable, timeout: Optional[float] = ..., chunksize: int = ...) -> typing.Iterable[Any]: ...
    def dispatch_next(self) -> None: ...
    def print_progress(self) -> None: ...
    def clear(self) -> None: ...
    def __len__(self) -> int: ...

def delayed(function: _F) -> Callable[..., Tuple[Callable, tuple, dict]]: ...
def cpu_count(only_physical_cores: bool = ...) -> int: ...
def effective_n_jobs(n_jobs: int = ...) -> int: ...
def hash(obj: Any, hash_name: str = ..., coerce_mmap: bool = ...) -> str: ...
def dump(value: Any, filename: Union[str, PathLikeStr], compress: Union[bool, int] = ..., protocol: Optional[int] = ..., cache_size: Optional[int] = ...) -> List[str]: ...
def load(filename: Union[str, PathLikeStr], mmap_mode: Optional[str] = ...) -> Any: ...
def register_parallel_backend(name: str, factory: Callable[..., ParallelBackendBase], make_default: bool = ...) -> None: ...

#### aiocache

Built for async applications using the `asyncio` framework, `aiocache` enables non-blocking caching operations. It provides both in-memory (`SimpleMemoryCache`) and distributed options (`RedisCache`, `MemcachedCache`).

- **Backends**: In-memory, Redis, Memcached
- **Async Decorators**: `@cached`, `@cached_stampede`, `@multi_cached`  
- **Serialization**: Pluggable, defaults to JSON
- **Best For**: Asynchronous web frameworks (FastAPI, Sanic), distributed caching

```pyi
### aiocache.pyi (Partial - Most important classes and decorators)

import typing
from typing import Any, Callable, Coroutine, Dict, List, Optional, Tuple, Type, Union

_F = typing.TypeVar("_F", bound=Callable[..., Any])

class BaseCache:
    NAME: str
    def __init__(self, serializer: Optional[BaseSerializer] = ..., plugins: Optional[List[BasePlugin]] = ..., namespace: Optional[str] = ..., timeout: float = ..., ttl: Optional[int] = ...) -> None: ...
    @classmethod
    def parse_uri_path(cls, path: str) -> Dict[str, str]: ...
    async def add(self, key: str, value: Any, ttl: Optional[int] = ..., dumps_fn: Optional[Callable[[Any], bytes]] = ..., namespace: Optional[str] = ..., timeout: Optional[int] = ...) -> bool: ...
    async def get(self, key: str, default: Optional[Any] = ..., loads_fn: Optional[Callable[[bytes], Any]] = ..., namespace: Optional[str] = ..., timeout: Optional[int] = ...) -> Any: ...
    async def multi_get(self, keys: List[str], loads_fn: Optional[Callable[[bytes], Any]] = ..., namespace: Optional[str] = ..., timeout: Optional[int] = ...) -> List[Any]: ...
    async def set(self, key: str, value: Any, ttl: Optional[int] = ..., dumps_fn: Optional[Callable[[Any], bytes]] = ..., namespace: Optional[str] = ..., timeout: Optional[int] = ..., _cas_token: Optional[Any] = ...) -> bool: ...
    async def multi_set(self, pairs: List[Tuple[str, Any]], ttl: Optional[int] = ..., dumps_fn: Optional[Callable[[Any], bytes]] = ..., namespace: Optional[str] = ..., timeout: Optional[int] = ...) -> bool: ...
    async def delete(self, key: str, namespace: Optional[str] = ..., timeout: Optional[int] = ...) -> int: ...
    async def exists(self, key: str, namespace: Optional[str] = ..., timeout: Optional[int] = ...) -> bool: ...
    async def increment(self, key: str, delta: int = ..., namespace: Optional[str] = ..., timeout: Optional[int] = ...) -> int: ...
    async def expire(self, key: str, ttl: Optional[int] = ..., namespace: Optional[str] = ..., timeout: Optional[int] = ...) -> bool: ...
    async def clear(self, namespace: Optional[str] = ..., timeout: Optional[int] = ...) -> bool: ...
    async def close(self, timeout: Optional[int] = ...) -> bool: ...
    async def raw(self, command: str, *args: Any, encoding: Optional[str] = ..., timeout: Optional[int] = ..., **kwargs: Any) -> Any: ...

class SimpleMemoryCache(BaseCache):
    NAME: str
    def __init__(self, serializer: Optional[BaseSerializer] = ..., **kwargs: Any) -> None: ...

class RedisCache(BaseCache):
    NAME: str
    def __init__(self, serializer: Optional[BaseSerializer] = ..., **kwargs: Any) -> None: ...

class MemcachedCache(BaseCache):
    NAME: str
    def __init__(self, serializer: Optional[BaseSerializer] = ..., **kwargs: Any) -> None: ...

class BaseSerializer:
    DEFAULT_ENCODING: Optional[str]
    def __init__(self, *args: Any, encoding: Union[str, object] = ..., **kwargs: Any) -> None: ...
    def dumps(self, value: Any) -> bytes: ...
    def loads(self, value: bytes) -> Any: ...

class JsonSerializer(BaseSerializer):
    def dumps(self, value: Any) -> str: ...
    def loads(self, value: str) -> Any: ...

class PickleSerializer(BaseSerializer):
    def dumps(self, value: Any) -> bytes: ...
    def loads(self, value: bytes) -> Any: ...

class NullSerializer(BaseSerializer):
    def dumps(self, value: Any) -> Any: ...
    def loads(self, value: Any) -> Any: ...

class BasePlugin:
    async def pre_get(self, client: BaseCache, key: str, namespace: Optional[str], **kwargs: Any) -> None: ...
    async def post_get(self, client: BaseCache, key: str, namespace: Optional[str], rv: Any, **kwargs: Any) -> None: ...
    # ... (and similar methods for other cache operations)

_Cache = TypeVar("_Cache", bound=BaseCache)

def cached(
    ttl: Optional[int] = ...,
    key: Optional[str] = ...,
    key_builder: Optional[Callable[..., str]] = ...,
    namespace: Optional[str] = ...,
    cache: Union[Type[_Cache], str] = ...,
    serializer: Optional[BaseSerializer] = ...,
    plugins: Optional[List[BasePlugin]] = ...,
    alias: Optional[str] = ...,
    noself: bool = ...,
    skip_cache_func: Optional[Callable[[Any], bool]] = ...,
    **kwargs: Any
) -> Callable[[_F], _F]: ...

def cached_stampede(
    lease: int = ...,
    ttl: Optional[int] = ...,
    key: Optional[str] = ...,
    key_builder: Optional[Callable[..., str]] = ...,
    namespace: Optional[str] = ...,
    cache: Union[Type[_Cache], str] = ...,
    serializer: Optional[BaseSerializer] = ...,
    plugins: Optional[List[BasePlugin]] = ...,
    alias: Optional[str] = ...,
    noself: bool = ...,
    skip_cache_func: Optional[Callable[[Any], bool]] = ...,
    **kwargs: Any
) -> Callable[[_F], _F]: ...

def multi_cached(
    keys_from_attr: Optional[str] = ...,
    namespace: Optional[str] = ...,
    key_builder: Optional[Callable[..., str]] = ...,
    ttl: Optional[int] = ...,
    cache: Union[Type[_Cache], str] = ...,
    serializer: Optional[BaseSerializer] = ...,
    plugins: Optional[List[BasePlugin]] = ...,
    alias: Optional[str] = ...,
    skip_cache_func: Optional[Callable[[str, Any], bool]] = ...,
    **kwargs: Any
) -> Callable[[_F], _F]: ...
```

### Summary of type hints

```pyi
### Type Stubs for Caching Libraries

from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Type,
    Iterable,
    Tuple,
    Union,
    TypeVar,
    Generic,
)
import datetime
import logging
from typing_extensions import Literal  # For older Python versions
```

*   **Generics:** For generic types like `Cache`, `FIFOCache`, `LFUCache`, etc. (in `cachetools`, `cachebox`, `klepto`) , I've used `TypeVar` to represent the key (`KT`) and value (`VT`) types.  This gives better type hinting.
*   **`object` as Default:** Where the original code uses implicit dynamic typing (no explicit type) or uses an internal implementation detail, I've often used `object` as the most general type hint.  This avoids creating stubs for internal classes.
*   **`NotImplementedError` and `typing.NoReturn`:** I've used `typing.NoReturn` for methods that are *not implemented* in a base class.  This is more precise than raising `NotImplementedError`, which would imply that a subclass *should* implement it.
*   **`defaultdict`:**  I've handled cases where `defaultdict` is used internally, providing a default factory function.
*   **`_Conn`:**  This internal helper class from `aiocache` is fully defined as all its methods are based on exported API.
* **`_DISTUTILS_PATCH`, `VIRTUALENV_PATCH_FILE`, etc.:** These internal constants/classes, used for patching `distutils`, are omitted.
*   **`kwargs` Handling:** In many cases, I've used `**kwargs` to represent arbitrary keyword arguments, especially when those arguments are passed directly to another function (like `open` or a backend-specific constructor).
* **`functools`:** The return type of decorators (`lru_cache`, `cache`) is `Callable[[Callable[..., R]], Callable[..., R]]`.  I've used a `TypeVar` named `_R` to make the relationship between the input and output types clear.
* **`klepto` classes**: Added the API for the `archive`, `dir_archive`, `sql_archive`, `sqltable_archive` based on the source code.
* **`joblib` classes**: Added the classes in the public API, `Memory`, `MemorizedFunc`, `NotMemorizedFunc`.

#### Recommendations

The best caching library depends on your specific needs - whether you require persistence, have large datasets, need multi-process safety, or are using an async framework. By understanding the strengths of each library, you can make an informed choice to optimize your application's performance.


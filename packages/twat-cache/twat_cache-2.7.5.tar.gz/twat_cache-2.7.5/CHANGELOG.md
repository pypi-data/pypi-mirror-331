---
this_file: CHANGELOG.md
---

# Changelog

All notable changes to the `twat_cache` package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v2.5.3] - 2025-03-04

### Added
- Enhanced hybrid caching capabilities
  - Improved automatic backend switching based on data characteristics
  - Added more intelligent data type detection
  - Optimized threshold determination for backend selection
- Expanded test coverage
  - Added more comprehensive tests for Redis engine
  - Improved test coverage for hybrid caching
  - Added tests for edge cases in backend selection
- Improved documentation
  - Updated README with more detailed examples
  - Added more comprehensive docstrings
  - Reorganized TODO list for better clarity and actionability

### Fixed
- Resolved several edge cases in Redis connection handling
- Fixed type annotation issues in context management
- Addressed potential race conditions in multi-threaded environments
- Improved error handling in serialization/deserialization processes

### Changed
- Refactored backend selection logic for better performance
- Improved context management API for more intuitive usage
- Updated dependencies to latest compatible versions
- Reorganized project structure for better maintainability

## [v2.3.0] - 2025-03-04

### Added
- Improved context management utilities
  - Enhanced error handling in context managers
  - Added support for explicit engine selection in context managers
  - Improved resource cleanup mechanisms
- Enhanced backend selection strategy
  - Refined data type detection for optimal backend selection
  - Added support for hybrid caching with automatic backend switching
  - Improved fallback mechanisms for unavailable backends
- Comprehensive documentation updates
  - Added detailed examples for all cache backends
  - Created documentation for context management
  - Updated installation and usage instructions

### Fixed
- Resolved remaining type compatibility issues across the codebase
- Fixed edge cases in Redis connection handling
- Addressed potential memory leaks in long-running cache instances
- Improved error handling in serialization/deserialization processes

### Changed
- Refactored internal cache key generation for better performance
- Standardized logging format across all cache engines
- Improved test coverage for all components
- Updated dependencies to latest compatible versions

## [v2.2.0] - 2024-09-01

### Added

- Comprehensive test suite for backend selection strategy
  - Tests for data size estimation
  - Tests for type-based backend selection
  - Tests for backend availability
  - Tests for various data types (primitive, containers, NumPy arrays, pandas DataFrames)
- Redis cache engine implementation
  - Full Redis cache engine with serialization, compression, and TTL support
  - Redis-specific configuration options
  - Proper connection handling and error management
  - Registration in the engine manager
- Documentation for cache context management
  - Detailed guide on using context managers
  - Examples for basic and advanced usage patterns
  - Best practices for resource management
  - Error handling recommendations

### Fixed

- Type compatibility issues in context.py with CacheConfig protocol
  - Updated protocol in type_defs.py to use validate_config instead of validate
  - Fixed type casting to avoid type errors
  - Improved type annotations for better static analysis
- Linter errors in engine implementations
  - Fixed import issues with optional dependencies
  - Addressed type compatibility warnings
  - Improved error handling in Redis engine

### Changed

- Expanded test coverage for cache engines
  - Added comprehensive tests for Redis cache engine
  - Tests for initialization, configuration validation, key generation
  - Tests for caching operations and error handling
- Refactored common patterns across engine implementations
  - Standardized engine initialization and validation procedures
  - Created unified interfaces for all cache backends
  - Improved code organization and maintainability

## [v2.1.1] - 2024-08-26

### Added

- New custom exceptions module with proper inheritance hierarchy
  - Base `TwatCacheError` exception class
  - Specialized exceptions for different error categories (configuration, engine, resource, etc.)
  - Improved error messages with context-specific information
- Context management for cache engines
  - `CacheContext` class that provides resource cleanup on exit
  - Safe resource management with proper error handling
  - Support for engine selection based on configuration
- Tests for exceptions and context management modules
  - Simple test suite for exception hierarchy and messages
  - Context management tests with mocking for proper isolation
- Implemented data type-based cache backend selection strategy
  - New `backend_selector` module for automatic backend selection
  - Helper functions for common data types (numpy, pandas, images, json)
  - Smart backend selection based on data characteristics
- Added hybrid caching capabilities
  - `hybrid_cache` decorator for size-based backend selection
  - `smart_cache` decorator for automatic backend selection
- Added example demonstrating the backend selection strategy
- Created CHANGELOG.md for tracking version changes
- Updated TODO.md to reflect completed items and reprioritize tasks

### Fixed

- Fixed error handling in various cache engines
- Improved cleanup logic for better resource management
- Made error messages more consistent across the codebase
- Installation issues with pip install -e . by replacing hatchling with setuptools
- Path handling in CacheContext

### Changed

- Standardized initialization patterns across engine implementations
- Improved shutdown procedures to properly release resources
- Removed setup.py in favor of pyproject.toml for modern Python packaging
- Refactored context manager implementation for better error handling 


## \[1.8.1] - 2025-02-18

### Added

* Added comprehensive type stubs for all cache engines
* Added detailed rationale section in README.md comparing different caching libraries
* Added extensive code examples for each caching strategy

### Changed

* Updated documentation with detailed type hints and protocols
* Improved error messages in cache engines
* Enhanced configuration validation

### Fixed

* Fixed type hints in async cache implementations
* Fixed decorator type hints for better IDE support
* Fixed linter errors in multiple files

### Issues

* Still missing type stubs for external dependencies
* Some linter warnings in test files need addressing
* Need to improve async test coverage

### Next Steps

1. Fix remaining linter issues:
   * Add missing type stubs for external dependencies
   * Address warnings in test files
   * Improve type safety in async code

2. Enhance test coverage:
   * Add more async test cases
   * Add stress tests for race conditions
   * Add integration tests for all backends

3. Improve documentation:
   * Add migration guide
   * Add performance comparison guide
   * Add troubleshooting section

## \[1.8.0] - 2025-02-17

### Added

* Completed core features:
  * Memory-based caching (mcache)
  * Disk-based caching (bcache)
  * File-based caching (fcache)
  * Async-capable caching (via ucache)
  * Universal caching (ucache)
* Implemented all cache engines:
  * FunctoolsCacheEngine (base memory cache)
  * CacheToolsEngine (flexible memory cache)
  * DiskCacheEngine (SQL-based disk cache)
  * JoblibEngine (file-based cache)
  * KleptoEngine (flexible cache)
  * AioCacheEngine (async cache)
* Added comprehensive features:
  * TTL support for all caches
  * Multiple eviction policies (LRU, LFU, FIFO, RR)
  * Secure file permissions for disk caches
  * Compression support for file caches
  * Race condition handling
  * Proper error handling and logging
* Added proper type hints and protocols
* Added comprehensive test suite
* Updated documentation with examples

### Changed

* Reorganized backend priorities for each decorator:
  * mcache: cachebox > cachetools > functools
  * bcache: diskcache > klepto SQL > mcache
  * fcache: joblib > klepto file > mcache
  * ucache: auto-selects best backend
* Enhanced test coverage with backend-specific tests
* Improved error handling and logging
* Updated configuration system to use Pydantic

### Fixed

* Fixed CacheConfig initialization issues
* Fixed cache stats tracking
* Fixed maxsize enforcement
* Fixed race conditions in multi-threaded scenarios
* Fixed file permissions for disk caches
* Fixed type hints and protocols

### Issues

* Missing type stubs for some dependencies:
  * aiocache
  * diskcache
  * joblib
  * klepto
* Some linter warnings in test files
* Need more async test coverage
* Need more stress tests for race conditions

### Next Steps

1. Type System:
   * Add missing type stubs for dependencies
   * Fix remaining linter warnings
   * Add more type safety

2. Testing:
   * Add more async tests
   * Add stress tests for race conditions
   * Add performance benchmarks
   * Add integration tests

3. Documentation:
   * Add API reference
   * Add performance guide
   * Add migration guide
   * Add troubleshooting guide

4. Performance:
   * Add caching statistics
   * Add cache warming
   * Add cache prefetching
   * Add cache compression options

5. Security:
   * Add encryption support
   * Add access control
   * Add audit logging
   * Add cache poisoning protection

## [1.7.9] - 2025-02-16

### Changed

* Updated TODO.md with clearer structure and priorities
* Reorganized Phase 2 tasks to focus on critical issues first
* Added more detailed subtasks for each component

### Fixed

* Fixed Pydantic field validators in CacheConfig
* Updated model\_config settings
* Improved error messages

### Issues

* Critical: CacheEngine import failing in test\_engines.py
* CacheConfig initialization still broken (TypeError: CacheConfig() takes no arguments)
* Cache stats tracking not working
* Cache maxsize enforcement not working
* Multiple linting issues identified:
  * Magic numbers in comparisons
  * Boolean argument type issues
  * Module naming conflicts with stdlib
  * Unused arguments in lambda functions
  * Complex function (clear\_cache)

### Next Steps

1. Fix Critical Engine Issues:
   * Fix CacheEngine import in base.py
   * Fix test\_engines.py import error
   * Fix CacheConfig initialization
   * Address linting issues

2. Fix Cache Engine Core:
   * Implement proper stats tracking
   * Fix maxsize enforcement
   * Add proper cache key generation
   * Add proper error handling

3. Improve Test Coverage:
   * Fix failing tests
   * Add engine-specific tests
   * Add performance benchmarks

4. Documentation:
   * Add configuration guide
   * Add backend selection guide
   * Add performance optimization guide

## [1.7.8] - 2025-02-16

### Changed

* Reorganized TODO.md with clearer structure and priorities
* Added Phase 3 for advanced features
* Updated test results analysis

### Fixed

* Fixed Pydantic field validators in CacheConfig
* Updated field validator decorators to use @classmethod
* Fixed model\_config settings

### Issues

* CacheConfig initialization still broken (TypeError: CacheConfig() takes no arguments)
* Cache stats tracking not working (hits/misses not being counted)
* Cache maxsize enforcement not working (cache growing beyond limit)
* Cache clearing behavior inconsistent
* Field validation in CacheConfig needs fixing

### Next Steps

1. Fix CacheConfig initialization:
   * Update Pydantic model to properly accept constructor arguments
   * Fix field validation and property access
   * Add proper error messages
   * Update model\_config for proper initialization

2. Fix cache engine issues:
   * Fix stats tracking in FunctoolsCacheEngine
   * Fix maxsize enforcement
   * Fix cache key generation
   * Fix cache clearing behavior

3. Fix failing tests:
   * Fix CacheConfig initialization tests
   * Fix cache stats tracking tests
   * Fix maxsize enforcement tests
   * Fix cache clearing tests

## [1.7.7] - 2025-02-16

### Changed

* Reorganized TODO.md to better reflect current priorities
* Updated CacheConfig implementation to use proper Pydantic fields
* Fixed linting issues in configuration system

### Fixed

* Removed leading underscores from CacheConfig field names
* Fixed field validation in CacheConfig
* Fixed property access in CacheConfig

### Issues

* CacheConfig initialization is broken (TypeError: CacheConfig() takes no arguments)
* Cache stats tracking is not working (hits/misses not being counted)
* Cache maxsize enforcement is not working (cache growing beyond limit)
* Cache clearing behavior is inconsistent
* Field validation in CacheConfig needs fixing

### Next Steps

1. Fix CacheConfig initialization:
   * Implement proper Pydantic model initialization
   * Fix field validation
   * Add proper error messages

2. Fix cache engine issues:
   * Fix stats tracking in FunctoolsCacheEngine
   * Fix maxsize enforcement
   * Fix cache key generation
   * Fix cache clearing behavior

3. Improve test coverage:
   * Add missing engine-specific tests
   * Add benchmark tests
   * Add stress tests
   * Add integration tests

## [1.7.6] - 2025-02-16

### Changed

* Reorganized TODO.md to better track progress
* Updated test suite with comprehensive engine tests
* Improved error handling in cache engines

### Fixed

* Renamed `lru.py` to `functools.py` for clarity
* Removed redundant SQL and Redis implementations
* Added proper type hints and docstrings

## [1.7.5] - 2025-02-15

### Fixed

* Fixed README.md formatting

## [1.7.3] - 2025-02-15

### Changed

* Minor documentation updates
* Internal code improvements

## [1.7.0] - 2025-02-13

### Added

* Added pyupgrade to development dependencies
* Added new fix command in pyproject.toml for automated code fixes
* Enhanced test environment with specific pytest dependencies
  * Added pytest-xdist for parallel test execution
  * Added pytest-benchmark for performance testing

### Changed

* Reorganized imports in core module
* Updated gitignore to exclude \_private directory

### Fixed

* Fixed import statement in **init**.py
* Improved development tooling configuration

## [1.6.2] - 2025-02-06

### Fixed

* Bug fixes and stability improvements

## [1.6.1] - 2025-02-06

### Changed

* Minor updates and improvements

## [1.6.0] - 2025-02-06

### Added

* Initial GitHub repository setup
* Comprehensive project structure
* Basic caching functionality
* Multiple backend support (memory, SQL, joblib)
* Automatic cache directory management
* Type hints and modern Python features

## [1.1.0] - 2025-02-03

### Added

* Early development version
* Core caching functionality

## [1.0.0] - 2025-02-03

### Added

* Initial release
* Basic memory caching implementation

## \[1.8.2] - 2025-02-19

### Changed

* Refocused project goals on simplicity and ease of use
* Streamlined TODO list to prioritize core functionality
* Reorganized implementation plan to focus on essential features

### Added

* Clear implementation status tracking in TODO.md
* Detailed testing strategy
* Documentation approach guidelines

### Removed

* Unnecessary complexity from implementation plan
* Redundant feature requests
* Overly complex API specifications

### Next Steps

1. Fix Critical Issues:
   * Remove magic numbers from tests
   * Fix boolean parameter warnings
   * Address unused imports
   * Fix function complexity issues

2. Improve Core Functionality:
   * Complete fallback mechanism
   * Add proper logging
   * Implement cache stats
   * Add inspection utilities

3. Enhance Testing:
   * Add test constants
   * Implement async tests
   * Add stress tests
   * Add backend-specific tests

[1.7.9]: https://github.com/twardoch/twat-cache/compare/v1.7.8...v1.7.9

[1.7.8]: https://github.com/twardoch/twat-cache/compare/v1.7.7...v1.7.8

[1.7.7]: https://github.com/twardoch/twat-cache/compare/v1.7.6...v1.7.7

[1.7.6]: https://github.com/twardoch/twat-cache/compare/v1.7.5...v1.7.6

[1.7.5]: https://github.com/twardoch/twat-cache/compare/v1.7.3...v1.7.5

[1.7.3]: https://github.com/twardoch/twat-cache/compare/v1.7.0...v1.7.3

[1.7.0]: https://github.com/twardoch/twat-cache/compare/v1.6.2...v1.7.0

[1.6.2]: https://github.com/twardoch/twat-cache/compare/v1.6.1...v1.6.2

[1.6.1]: https://github.com/twardoch/twat-cache/compare/v1.6.0...v1.6.1

[1.6.0]: https://github.com/twardoch/twat-cache/compare/v1.1.0...v1.6.0

[1.1.0]: https://github.com/twardoch/twat-cache/compare/v1.0.0...v1.1.0

[1.0.0]: https://github.com/twardoch/twat-cache/releases/tag/v1.0.0

# Development Log

### Completed

* Updated TODO.md with clearer structure and priorities
* Fixed Pydantic field validators
* Updated model\_config settings
* Identified critical import issue in test\_engines.py

### In Progress

* Fixing CacheEngine import issue
* Fixing CacheConfig initialization
* Addressing linting issues
* Improving test coverage

### Next Steps

1. Fix Critical Issues:
   * Fix CacheEngine import
   * Fix CacheConfig initialization
   * Fix test failures
   * Address linting issues

2. Improve Core Functionality:
   * Fix stats tracking
   * Fix maxsize enforcement
   * Improve cache key generation
   * Add proper error handling

3. Enhance Testing:
   * Fix failing tests
   * Add comprehensive test suite
   * Add performance benchmarks

# Critical Considerations

1. Engine System:
   * CacheEngine must be properly exported from base.py
   * All engines must properly implement the base interface
   * Stats tracking must be consistent across all engines

2. Configuration System:
   * CacheConfig must properly initialize with constructor arguments
   * Field validation must be robust and informative
   * Cache directory management must be reliable

3. Testing System:
   * All engines must be properly tested
   * Performance benchmarks must be comprehensive
   * Error handling must be thoroughly tested

## [1.7.8]: https://github.com/twardoch/twat-cache/compare/v1.7.7...v1.7.8

## [1.7.7]: https://github.com/twardoch/twat-cache/compare/v1.7.6...v1.7.7

## [1.7.6]: https://github.com/twardoch/twat-cache/compare/v1.7.5...v1.7.6

## [1.7.5]: https://github.com/twardoch/twat-cache/compare/v1.7.3...v1.7.5

## [1.7.3]: https://github.com/twardoch/twat-cache/compare/v1.7.0...v1.7.3

## [1.7.0]: https://github.com/twardoch/twat-cache/compare/v1.6.2...v1.7.0

## [1.6.2]: https://github.com/twardoch/twat-cache/compare/v1.6.1...v1.6.2

## [1.6.1]: https://github.com/twardoch/twat-cache/compare/v1.6.0...v1.6.1

## [1.6.0]: https://github.com/twardoch/twat-cache/compare/v1.1.0...v1.6.0

## [1.1.0]: https://github.com/twardoch/twat-cache/compare/v1.0.0...v1.1.0

## [1.0.0]: https://github.com/twardoch/twat-cache/releases/tag/v1.0.0

# Development Log

### Completed

* Fixed Pydantic field validators in CacheConfig:
  * Updated validators to use @classmethod decorator
  * Fixed model\_config settings
  * Improved error messages
* Reorganized TODO.md:
  * Added clearer structure
  * Prioritized critical fixes
  * Added Phase 3 for advanced features
* Updated test suite:
  * Added more comprehensive test cases
  * Identified failing tests
  * Added test categories

### In Progress

* Fixing CacheConfig initialization issues:
  * Working on proper Pydantic model setup
  * Fixing field validation and property access
  * Adding proper error messages
* Fixing cache engine issues:
  * Implementing proper stats tracking
  * Fixing maxsize enforcement
  * Improving cache key generation
  * Fixing cache clearing behavior

### Next Steps

1. Fix Critical Issues:
   * Fix CacheConfig initialization
   * Fix cache stats tracking
   * Fix maxsize enforcement
   * Fix cache clearing behavior

2. Enhance Test Coverage:
   * Fix failing tests
   * Add missing engine-specific tests
   * Add performance tests

3. Improve Documentation:
   * Update configuration guide
   * Add troubleshooting guide
   * Add performance tips
   * Add examples

# Critical Considerations

1. Configuration System:
   * CacheConfig must properly initialize with constructor arguments
   * Field validation must work correctly
   * Property access must be reliable
   * Error messages must be helpful

2. Cache Engine Behavior:
   * Stats tracking must be accurate
   * Maxsize enforcement must be reliable
   * Cache clearing must be consistent
   * Key generation must handle all types

3. Test Coverage:
   * All critical functionality must be tested
   * Edge cases must be covered
   * Performance must be verified
   * Error handling must be tested

# Conslidation UI Project Analysis & Plan

## Progress Log

### 2024-03-21

* Updated TODO.md with completed tasks and reorganized remaining work
* Major progress in core functionality:
  * Completed all basic cache engine implementations
  * Fixed cache stats tracking and clearing behavior
  * Improved type hints and configuration system
  * Added comprehensive test coverage for core features
* Next steps prioritized:
  1. Add missing engine-specific tests (eviction, concurrency, etc.)
  2. Implement serialization protocol
  3. Add async test coverage
  4. Create comprehensive documentation

Critical Considerations:

1. Engine-specific Tests:
   * Need stress tests for memory limits and eviction policies
   * Add concurrent access testing with high load
   * Test edge cases like cache corruption and recovery
   * Verify proper cleanup of resources

2. Serialization Protocol:
   * Add support for complex objects and custom types
   * Consider compression for large cached values
   * Implement versioning for cached data format
   * Add validation for serialized data integrity

3. Async Support:
   * Improve error handling for timeouts and connection issues
   * Ensure proper cleanup of async resources
   * Add retry mechanisms for transient failures
   * Test interaction with different event loops

4. Documentation:
   * Add detailed performance characteristics
   * Document tradeoffs between different cache engines
   * Create troubleshooting guide
   * Add migration guide for users of removed implementations

## Recent Changes

### 2024-03-21

* Fixed CacheConfig implementation:
  * Added proper field aliases for configuration parameters
  * Implemented abstract base class methods
  * Added Pydantic model configuration for proper field handling
  * Fixed validation method
* Updated test suite:
  * Fixed failing tests related to CacheConfig instantiation
  * Added tests for field aliases and validation
  * Improved test coverage for configuration handling

### Next Steps

1. Fix remaining test failures:
   * Cache stats tracking
   * List/unhashable type handling
   * Cache clearing behavior
2. Implement missing engine-specific tests:
   * Test cache eviction policies
   * Test concurrent access
   * Test error handling
   * Test serialization/deserialization
   * Test memory limits

### Critical Considerations

1. Engine-specific Tests:
   * Need stress tests for memory limits and eviction policies
   * Add concurrent access testing with high load
   * Test edge cases like cache corruption and recovery
   * Verify proper cleanup of resources

2. Serialization Protocol:
   * Add support for complex objects and custom types
   * Consider compression for large cached values
   * Implement versioning for cached data format
   * Add validation for serialized data integrity

3. Async Support:
   * Improve error handling for timeouts and connection issues
   * Ensure proper cleanup of async resources
   * Add retry mechanisms for transient failures
   * Test interaction with different event loops

4. Documentation:
   * Add detailed performance characteristics
   * Document tradeoffs between different cache engines
   * Create troubleshooting guide
   * Add migration guide for users of removed implementations

### 2024-03-19

#### Current Status

* Ran development setup and tests
* Found critical issues that need immediate attention:
  1. Pydantic field validator errors in CacheConfig
  2. 27 remaining linting issues
  3. Test failures across all test files

#### Critical Issues

1. **Pydantic Integration Issues**
   * Error: `@field_validator` cannot be applied to instance methods

   * Location: `src/twat_cache/config.py`

   * Impact: Breaking all tests due to config initialization failure

2. **Linting Issues**
   * 27 remaining issues including:

     * Magic numbers in comparisons
     * Print statements in production code
     * Boolean positional arguments
     * Module naming conflicts
     * Complex function warnings

#### Next Steps

1. **Immediate Fixes**
   * Fix Pydantic field validator implementation in CacheConfig
   * Address critical linting issues affecting functionality
   * Fix test failures

2. **Short-term Tasks**
   * Complete cache stats tracking implementation
   * Add proper type constraints
   * Implement missing test cases

3. **Documentation Updates**
   * Document configuration system
   * Add validation rules
   * Update type hints documentation

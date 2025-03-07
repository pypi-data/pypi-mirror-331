# this_file: tests/test_constants.py
"""Constants used in tests."""

# Cache sizes
SMALL_CACHE_SIZE = 10
DEFAULT_CACHE_SIZE = 100
LARGE_CACHE_SIZE = 1000

# TTL values
SHORT_TTL = 1
DEFAULT_TTL = 60
LONG_TTL = 3600

# Test values
TEST_VALUE = 5
TEST_RESULT = TEST_VALUE * TEST_VALUE
TEST_LIST = [1, 2, 3, 4, 5]
TEST_LIST_SUM = 15
TEST_CALL_COUNT = 2

# File permissions
TEST_PERMISSIONS = 0o700

# Compression levels
DEFAULT_COMPRESSION = 6
NO_COMPRESSION = 0

# Cache stats
INITIAL_HITS = 0
INITIAL_MISSES = 0

# Test data sizes
SMALL_DATA_SIZE = 1024  # 1KB
DEFAULT_DATA_SIZE = 1024 * 1024  # 1MB
LARGE_DATA_SIZE = 10 * 1024 * 1024  # 10MB

# Timeouts
SHORT_TIMEOUT = 0.1
DEFAULT_TIMEOUT = 1.0
LONG_TIMEOUT = 5.0

# File paths
TEST_FOLDER = "test_cache"
TEST_FILE = "test_data.cache"
TEST_DB = "test_cache.db"

# Test data
TEST_KEY = "test_key"
TEST_BOOL = True
TEST_INT = 123

# Call counts
EXPECTED_CALLS_SINGLE = 1
EXPECTED_CALLS_DOUBLE = 2
EXPECTED_CALLS_TRIPLE = 3
# this_file: tests/test_constants.py
"""Constants used in test files to avoid magic numbers."""

# Cache sizes
SMALL_CACHE_SIZE = 10
DEFAULT_CACHE_SIZE = 100
LARGE_CACHE_SIZE = 1000

# TTL values (in seconds)
SHORT_TTL = 0.1
DEFAULT_TTL = 3600
LONG_TTL = 86400

# Test values
TEST_KEY = "test_key"
TEST_VALUE = 42
TEST_RESULT = 84  # TEST_VALUE * 2

# File permissions
DIR_PERMISSIONS = 0o700
FILE_PERMISSIONS = 0o600

# Compression levels
MIN_COMPRESSION = 0
DEFAULT_COMPRESSION = 6
MAX_COMPRESSION = 9

# Cache stats
INITIAL_HITS = 0
INITIAL_MISSES = 0
INITIAL_SIZE = 0

# Test data sizes
SMALL_DATA_SIZE = 1000
MEDIUM_DATA_SIZE = 100000
LARGE_DATA_SIZE = 1000000

# Test timeouts
SHORT_TIMEOUT = 0.1
DEFAULT_TIMEOUT = 1.0
LONG_TIMEOUT = 5.0

# Test file paths
TEST_CACHE_DIR = "test_cache"
TEST_DB_FILE = "test.db"
TEST_ARRAY_FILE = "test_array.npy"

# Test data
TEST_LIST = [1, 2, 3, 4, 5]
TEST_LIST_SUM = 15

# Cache keys
TEST_BOOL = True
TEST_INT = 123

# Call counts
EXPECTED_CALLS_SINGLE = 1
EXPECTED_CALLS_DOUBLE = 2
EXPECTED_CALLS_TRIPLE = 3
EXPECTED_CALLS_QUAD = 4

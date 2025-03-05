# this_file: tests/test_fallback.py
"""Tests for backend selection and fallback behavior."""

import asyncio
from unittest.mock import patch

import pytest

from twat_cache.decorators import (
    _get_available_backends,
    _select_best_backend,
    mcache,
    bcache,
    acache,
    ucache,
)
from tests.test_constants import (
    CACHE_SIZE,
    EXPECTED_CALLS_SINGLE,
    SQUARE_INPUT,
    SQUARE_RESULT,
)


def test_backend_availability() -> None:
    """Test backend availability detection."""
    available = _get_available_backends()
    assert isinstance(available, dict)
    assert "functools" in available
    assert available["functools"] is True  # Always available


def test_backend_selection_preferred() -> None:
    """Test backend selection with preferred engine."""
    # Test with available preferred engine
    backend = _select_best_backend(preferred="functools")
    assert backend == "functools"

    # Test with unavailable preferred engine
    backend = _select_best_backend(preferred="nonexistent")
    assert backend == "functools"  # Should fallback to functools


def test_backend_selection_async() -> None:
    """Test backend selection for async functions."""
    # Test with aiocache available
    with patch.dict("sys.modules", {"aiocache": object()}):
        backend = _select_best_backend(is_async=True)
        assert backend == "aiocache"

    # Test without aiocache
    with patch.dict("sys.modules", {"aiocache": None}):
        backend = _select_best_backend(is_async=True)
        assert backend == "functools"  # Should fallback to functools


def test_backend_selection_disk() -> None:
    """Test backend selection for disk storage."""
    # Test with diskcache available
    with patch.dict("sys.modules", {"diskcache": object()}):
        backend = _select_best_backend(needs_disk=True)
        assert backend == "diskcache"

    # Test with joblib available
    with patch.dict("sys.modules", {"diskcache": None, "joblib": object()}):
        backend = _select_best_backend(needs_disk=True)
        assert backend == "joblib"

    # Test with klepto available
    with patch.dict(
        "sys.modules", {"diskcache": None, "joblib": None, "klepto": object()}
    ):
        backend = _select_best_backend(needs_disk=True)
        assert backend == "klepto"

    # Test with no disk backends
    with patch.dict("sys.modules", {"diskcache": None, "joblib": None, "klepto": None}):
        backend = _select_best_backend(needs_disk=True)
        assert backend == "functools"  # Should fallback to functools


def test_memory_cache_fallback() -> None:
    """Test memory cache fallback behavior."""
    call_count = 0

    @mcache(maxsize=CACHE_SIZE)
    def test_func(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * x

    # Should work even with no optional backends
    with patch.dict(
        "sys.modules",
        {
            "cachebox": None,
            "cachetools": None,
        },
    ):
        result = test_func(SQUARE_INPUT)
        assert result == SQUARE_RESULT
        assert call_count == EXPECTED_CALLS_SINGLE


def test_disk_cache_fallback() -> None:
    """Test disk cache fallback behavior."""
    call_count = 0

    @bcache(maxsize=CACHE_SIZE)
    def test_func(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * x

    # Should work even with no disk backends
    with patch.dict(
        "sys.modules",
        {
            "diskcache": None,
            "joblib": None,
            "klepto": None,
        },
    ):
        result = test_func(SQUARE_INPUT)
        assert result == SQUARE_RESULT
        assert call_count == EXPECTED_CALLS_SINGLE


@pytest.mark.asyncio
async def test_async_cache_fallback() -> None:
    """Test async cache fallback behavior."""
    call_count = 0

    @acache(maxsize=CACHE_SIZE)
    async def test_func(x: int) -> int:
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0.1)
        return x * x

    # Should work even without aiocache
    with patch.dict("sys.modules", {"aiocache": None}):
        result = await test_func(SQUARE_INPUT)
        assert result == SQUARE_RESULT
        assert call_count == EXPECTED_CALLS_SINGLE


def test_universal_cache_fallback() -> None:
    """Test universal cache fallback behavior."""
    call_count = 0

    @ucache(maxsize=CACHE_SIZE)
    def test_func(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * x

    # Should work with no optional backends
    with patch.dict(
        "sys.modules",
        {
            "cachebox": None,
            "cachetools": None,
            "diskcache": None,
            "joblib": None,
            "klepto": None,
            "aiocache": None,
        },
    ):
        result = test_func(SQUARE_INPUT)
        assert result == SQUARE_RESULT
        assert call_count == EXPECTED_CALLS_SINGLE


def test_backend_selection_priority() -> None:
    """Test backend selection priority order."""
    # Test memory cache priority
    with patch.dict(
        "sys.modules",
        {
            "cachebox": object(),
            "cachetools": object(),
        },
    ):
        backend = _select_best_backend()
        assert backend == "cachebox"  # Should prefer cachebox over cachetools

    # Test disk cache priority
    with patch.dict(
        "sys.modules",
        {
            "diskcache": object(),
            "joblib": object(),
            "klepto": object(),
        },
    ):
        backend = _select_best_backend(needs_disk=True)
        assert backend == "diskcache"  # Should prefer diskcache over others


def test_backend_selection_requirements() -> None:
    """Test backend selection based on requirements."""
    # Test async requirement overrides disk
    with patch.dict(
        "sys.modules",
        {
            "aiocache": object(),
            "diskcache": object(),
        },
    ):
        backend = _select_best_backend(is_async=True, needs_disk=True)
        assert backend == "aiocache"  # Should prefer aiocache for async

    # Test disk requirement with no async
    with patch.dict(
        "sys.modules",
        {
            "aiocache": object(),
            "diskcache": object(),
        },
    ):
        backend = _select_best_backend(needs_disk=True)
        assert backend == "diskcache"  # Should prefer diskcache for disk

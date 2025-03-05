#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "platformdirs",
#   "loguru",
# ]
# ///
# this_file: src/twat_cache/paths.py

"""
Path management utilities for twat-cache.

This module handles cache directory management, providing a unified interface
for determining and creating cache directories across different platforms.
"""

from pathlib import Path
import uuid
from loguru import logger
import shutil

try:
    import platformdirs

    HAS_PLATFORMDIRS = True
except ImportError:
    HAS_PLATFORMDIRS = False
    logger.warning("platformdirs not available, falling back to ~/.cache")


def get_cache_path(
    folder_name: str | None = None,
    *,
    create: bool = True,
    use_temp: bool = False,
) -> Path:
    """
    Get the path to a cache directory.

    Args:
        folder_name: Optional name for the cache folder. If None, a default
            location will be used.
        create: Whether to create the directory if it doesn't exist.
            Defaults to True.
        use_temp: Whether to use a temporary directory instead of the
            user's cache directory. Defaults to False.

    Returns:
        The path to the cache directory.

    Raises:
        ValueError: If the cache path is invalid or cannot be created.
    """
    if folder_name is None:
        folder_name = f"twat_cache_{uuid.uuid4().hex[:8]}"

    if use_temp:
        import tempfile

        base_path = Path(tempfile.gettempdir()) / "twat_cache"
    elif HAS_PLATFORMDIRS:
        base_path = Path(platformdirs.user_cache_dir("twat_cache"))
    else:
        base_path = Path.home() / ".cache" / "twat_cache"

    cache_path = base_path / folder_name

    if create and not cache_path.exists():
        try:
            cache_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created cache directory: {cache_path}")
        except Exception as e:
            logger.error(f"Failed to create cache directory {cache_path}: {e}")
            raise

    return cache_path


def validate_cache_path(path: str | Path) -> None:
    """
    Validate that a cache path is usable.

    Args:
        path: Path to validate

    Raises:
        ValueError: If the path is invalid or unusable
    """
    try:
        path = Path(path).resolve()
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        elif not path.is_dir():
            msg = f"Path exists but is not a directory: {path}"
            raise ValueError(msg)
    except Exception as e:
        msg = f"Invalid cache path {path}: {e}"
        raise ValueError(msg) from e


def clear_cache(folder_name: str | None = None) -> None:
    """
    Clear the cache directory for the given folder name.

    Args:
        folder_name: Name of the cache folder to clear. If None, clears all caches.

    Example:
        ```python
        clear_cache("my_cache")  # Clear specific cache
        clear_cache()  # Clear all caches
        ```
    """
    if folder_name:
        cache_path = get_cache_path(folder_name, create=False)
        if cache_path.exists():
            try:
                for item in cache_path.iterdir():
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                logger.info(f"Cleared cache directory: {cache_path}")
            except Exception as e:
                logger.error(f"Failed to clear cache directory {cache_path}: {e}")
                raise
    else:
        # Clear all caches
        base_paths = []
        if HAS_PLATFORMDIRS:
            base_paths.append(Path(platformdirs.user_cache_dir("twat_cache")))
        base_paths.append(Path.home() / ".cache" / "twat_cache")

        for base_path in base_paths:
            if base_path.exists():
                try:
                    import shutil

                    shutil.rmtree(base_path)
                    logger.info(f"Cleared cache base directory: {base_path}")
                except Exception as e:
                    logger.error(
                        f"Failed to clear cache base directory {base_path}: {e}"
                    )
                    raise

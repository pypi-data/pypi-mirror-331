#!/usr/bin/env python3
# this_file: src/twat_cache/logging.py

"""
Centralized logging configuration for twat_cache.

This module provides a configured logger instance that can be imported
and used throughout the package. It supports:
- Console logging with configurable level via TWAT_CACHE_LOG_LEVEL env var
- Optional file logging via TWAT_CACHE_LOG_FILE env var
- Structured logging with context information
"""

import os
import sys
from pathlib import Path

from loguru import logger

# Remove default handler
logger.remove()

# Get log level from environment or use INFO as default
LOG_LEVEL = os.environ.get("TWAT_CACHE_LOG_LEVEL", "INFO").upper()

# Add console handler with appropriate level
logger.add(
    sys.stderr,
    level=LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)

# Setup file logging if enabled
if os.environ.get("TWAT_CACHE_LOG_FILE", "0") == "1":
    try:
        # Determine log directory
        xdg_cache_home = os.environ.get("XDG_CACHE_HOME")
        if xdg_cache_home:
            log_dir = Path(xdg_cache_home) / "logs"
        else:
            log_dir = Path.home() / ".cache" / "logs"

        # Create log directory if it doesn't exist
        log_dir.mkdir(parents=True, exist_ok=True)

        # Add file handler
        log_file = log_dir / "twat_cache.log"
        logger.add(
            str(log_file),
            rotation="10 MB",
            retention="1 week",
            compression="gz",
            level=LOG_LEVEL,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        )
        logger.info(f"File logging enabled at {log_file}")
    except Exception as e:
        # Fall back to console-only logging if file setup fails
        logger.warning(f"Failed to setup file logging: {e}")
        logger.info("Falling back to console-only logging")

# Export the configured logger
__all__ = ["logger"]

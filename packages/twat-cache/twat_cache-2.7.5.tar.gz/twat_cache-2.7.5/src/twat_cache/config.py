#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "loguru",
#   "pydantic",
# ]
# ///
# this_file: src/twat_cache/config.py

"""Cache configuration system."""

import os
from typing import Any
from collections.abc import Callable

from pydantic import BaseModel, Field, field_validator

# Type aliases
EvictionPolicy = str | None
CacheType = str | None


class CacheConfig(BaseModel):
    """Cache configuration settings."""

    maxsize: int | None = Field(default=None, ge=1)
    folder_name: str | None = None
    preferred_engine: str | None = None
    serializer: Callable[[Any], str] | None = None
    cache_type: CacheType | None = None
    ttl: float | None = Field(default=None, ge=0)
    policy: EvictionPolicy = "lru"
    cache_dir: str | None = None  # For backward compatibility

    # Boolean fields
    use_sql: bool = False
    compress: bool = False
    secure: bool = True

    # Redis-specific configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None

    class Config:
        """Pydantic model configuration."""

        validate_assignment = True
        extra = "forbid"

    @classmethod
    @field_validator("maxsize")
    def validate_maxsize(cls, v: int | None) -> int | None:
        """Validate maxsize field."""
        if v is not None and v <= 0:
            msg = "maxsize must be positive"
            raise ValueError(msg)
        return v

    @classmethod
    @field_validator("ttl")
    def validate_ttl(cls, v: float | None) -> float | None:
        """Validate ttl field."""
        if v is not None and v < 0:
            msg = "ttl must be non-negative"
            raise ValueError(msg)
        return v

    @classmethod
    @field_validator("policy")
    def validate_policy(cls, v: EvictionPolicy) -> EvictionPolicy:
        """Validate policy field."""
        valid_policies = {"lru", "lfu", "fifo", "rr", "ttl"}
        if v is not None and v not in valid_policies:
            msg = f"policy must be one of {valid_policies}"
            raise ValueError(msg)
        return v

    @classmethod
    @field_validator("redis_port")
    def validate_redis_port(cls, v: int) -> int:
        """Validate redis_port field."""
        if v <= 0 or v > 65535:
            msg = f"redis_port must be between 1 and 65535, got {v}"
            raise ValueError(msg)
        return v

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "maxsize": self.maxsize,
            "folder_name": self.folder_name,
            "preferred_engine": self.preferred_engine,
            "serializer": self.serializer,
            "cache_type": self.cache_type,
            "ttl": self.ttl,
            "policy": self.policy,
            "use_sql": self.use_sql,
            "compress": self.compress,
            "secure": self.secure,
            "cache_dir": self.cache_dir,
            "redis_host": self.redis_host,
            "redis_port": self.redis_port,
            "redis_db": self.redis_db,
            "redis_password": self.redis_password,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CacheConfig":
        """Create configuration from dictionary."""
        return cls(**data)

    # Methods required by the CacheConfig protocol
    def get_maxsize(self) -> int | None:
        """Get the maxsize value."""
        return self.maxsize

    def get_folder_name(self) -> str | None:
        """Get the folder name."""
        return self.folder_name

    def get_use_sql(self) -> bool:
        """Get the use_sql value."""
        return self.use_sql

    def get_preferred_engine(self) -> str | None:
        """Get the preferred engine."""
        return self.preferred_engine

    def get_cache_type(self) -> str | None:
        """Get the cache type."""
        return self.cache_type

    # Redis-specific getters
    def get_redis_host(self) -> str:
        """Get the Redis host."""
        return os.environ.get("TWAT_CACHE_REDIS_HOST", self.redis_host)

    def get_redis_port(self) -> int:
        """Get the Redis port."""
        port_str = os.environ.get("TWAT_CACHE_REDIS_PORT")
        if port_str:
            try:
                return int(port_str)
            except ValueError:
                return self.redis_port
        return self.redis_port

    def get_redis_db(self) -> int:
        """Get the Redis database number."""
        db_str = os.environ.get("TWAT_CACHE_REDIS_DB")
        if db_str:
            try:
                return int(db_str)
            except ValueError:
                return self.redis_db
        return self.redis_db

    def get_redis_password(self) -> str | None:
        """Get the Redis password."""
        return os.environ.get("TWAT_CACHE_REDIS_PASSWORD", self.redis_password)

    # We can't override the validate method as it conflicts with Pydantic's validate
    # Instead, we'll implement a protocol-compatible method with a different name
    def validate_config(self) -> None:
        """Validate the configuration (protocol compatibility method)."""
        # This is handled by Pydantic validators


def create_cache_config(
    maxsize: int | None = None,
    folder_name: str | None = None,
    preferred_engine: str | None = None,
    serializer: Callable[[Any], str] | None = None,
    cache_type: CacheType | None = None,
    ttl: float | None = None,
    policy: EvictionPolicy = "lru",
    cache_dir: str | None = None,  # For backward compatibility
    *,  # Force remaining arguments to be keyword-only
    use_sql: bool = False,
    compress: bool = False,
    secure: bool = True,
    redis_host: str = "localhost",
    redis_port: int = 6379,
    redis_db: int = 0,
    redis_password: str | None = None,
) -> CacheConfig:
    """Create a cache configuration.

    Args:
        maxsize: Maximum size of the cache. None means unlimited.
        folder_name: Name of the cache folder.
        preferred_engine: Preferred cache engine.
        serializer: Function to serialize cache keys.
        cache_type: Type of cache to use.
        ttl: Time-to-live in seconds.
        policy: Cache eviction policy.
        cache_dir: Cache directory (deprecated).
        use_sql: Whether to use SQL backend.
        compress: Whether to compress cached data.
        secure: Whether to use secure file permissions.
        redis_host: Redis server hostname.
        redis_port: Redis server port.
        redis_db: Redis database number.
        redis_password: Redis server password.

    Returns:
        CacheConfig: Cache configuration object.

    Raises:
        ValueError: If configuration is invalid.
    """
    return CacheConfig(
        maxsize=maxsize,
        folder_name=folder_name,
        preferred_engine=preferred_engine,
        serializer=serializer,
        cache_type=cache_type,
        ttl=ttl,
        policy=policy,
        use_sql=use_sql,
        compress=compress,
        secure=secure,
        cache_dir=cache_dir,
        redis_host=redis_host,
        redis_port=redis_port,
        redis_db=redis_db,
        redis_password=redis_password,
    )

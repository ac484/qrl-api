"""
Redis client package
--------------------
Provides the async RedisClient and shared redis_client instance.
"""
from .client import RedisClient, redis_client

__all__ = ["RedisClient", "redis_client"]

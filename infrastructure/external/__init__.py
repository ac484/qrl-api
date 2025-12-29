"""
External API clients and integrations
Structured into mexc_client/ and redis_client/ packages per README layout.
Optional Redis client import to avoid hard dependency during lightweight usage or tests.
"""
from infrastructure.external.mexc_client import MEXCClient, mexc_client

RedisClient = None
redis_client = None
try:
    from infrastructure.external.redis_client import RedisClient as _RedisClient, redis_client as _redis_client

    RedisClient = _RedisClient
    redis_client = _redis_client
except Exception:
    # Redis support is optional; skip import errors when dependency is absent
    pass

__all__ = ["MEXCClient", "mexc_client"]
if RedisClient is not None:
    __all__.extend(["RedisClient", "redis_client"])

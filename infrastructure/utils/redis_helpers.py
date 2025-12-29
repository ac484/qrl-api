"""Helpers around Redis client operations with connection checks."""
from typing import Any, Dict, Optional
from infrastructure.external.redis_client.client import redis_client


async def get_if_connected(method_name: str, *args, **kwargs) -> Optional[Any]:
    """Call a RedisClient coroutine only when connected."""
    if not getattr(redis_client, "connected", False):
        return None
    method = getattr(redis_client, method_name, None)
    if not method:
        return None
    return await method(*args, **kwargs)


async def cache_json(key: str, data: Dict[str, Any]) -> bool:
    """Cache JSON-compatible mapping when Redis is available."""
    if not getattr(redis_client, "connected", False):
        return False
    try:
        await redis_client.client.set(key, data)
        return True
    except Exception:
        return False


__all__ = ["get_if_connected", "cache_json"]

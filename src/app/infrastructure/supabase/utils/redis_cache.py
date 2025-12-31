"""
Redis-backed cache helpers to reduce Supabase read pressure.
"""
import json
import logging
from typing import Any, Dict, List, Optional

from src.app.infrastructure.persistence.redis.client import RedisClient, redis_client

logger = logging.getLogger(__name__)


class RedisCache:
    def __init__(self, client: RedisClient = redis_client) -> None:
        self.client = client

    async def ensure_connection(self) -> bool:
        if not self.client.connected:
            return await self.client.connect()
        return True

    async def set_recent(self, key: str, values: List[Dict[str, Any]], ttl: int = 60) -> bool:
        """
        Store a JSON list in Redis with a TTL.
        """
        if not await self.ensure_connection() or self.client.client is None:
            logger.info("Redis connection unavailable; skipping cache set for %s", key)
            return False
        await self.client.client.set(key, json.dumps(values), ex=ttl)
        return True

    async def get_recent(self, key: str) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve and decode a cached JSON list from Redis.
        """
        if not await self.ensure_connection() or self.client.client is None:
            logger.info("Redis connection unavailable; skipping cache get for %s", key)
            return None

        raw = await self.client.client.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Failed to decode cached payload for %s", key)
            return None


__all__ = ["RedisCache"]

"""
Redis data manager extracted from redis_helpers_core for reuse.
"""
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class RedisDataManager:
    """Generic Redis data manager that handles serialization and logging."""

    def __init__(self, redis_client):
        self.client = redis_client

    async def set_json_data(
        self,
        key: str,
        data: Dict[str, Any],
        ttl: Optional[int] = None,
        add_timestamp: bool = True,
        operation_name: str = "Set data",
    ) -> bool:
        try:
            if add_timestamp:
                data["timestamp"] = datetime.now().isoformat()
                data["stored_at"] = int(datetime.now().timestamp() * 1000)

            json_data = json.dumps(data)
            if ttl:
                await self.client.setex(key, ttl, json_data)
            else:
                await self.client.set(key, json_data)

            logger.debug(f"{operation_name} successful: {key}")
            return True
        except Exception as exc:  # pragma: no cover - thin wrapper
            logger.error(f"{operation_name} failed for key {key}: {exc}")
            return False

    async def get_json_data(
        self,
        key: str,
        default: Any = None,
        operation_name: str = "Get data",
    ) -> Optional[Dict[str, Any]]:
        try:
            data = await self.client.get(key)
            if data:
                return json.loads(data)
            return default
        except Exception as exc:  # pragma: no cover - thin wrapper
            logger.error(f"{operation_name} failed for key {key}: {exc}")
            return default

    async def set_hash_data(self, key: str, data: Dict[str, Any], operation_name: str = "Set hash") -> bool:
        try:
            string_data = {k: str(v) for k, v in data.items()}
            await self.client.hset(key, mapping=string_data)
            logger.debug(f"{operation_name} successful: {key}")
            return True
        except Exception as exc:  # pragma: no cover - thin wrapper
            logger.error(f"{operation_name} failed for key {key}: {exc}")
            return False

    async def get_hash_data(self, key: str, operation_name: str = "Get hash") -> Dict[str, str]:
        try:
            return await self.client.hgetall(key)
        except Exception as exc:  # pragma: no cover - thin wrapper
            logger.error(f"{operation_name} failed for key {key}: {exc}")
            return {}

    async def add_to_sorted_set(
        self,
        key: str,
        value: Any,
        score: float,
        max_items: Optional[int] = None,
        operation_name: str = "Add to sorted set",
    ) -> bool:
        try:
            if isinstance(value, dict):
                value = json.dumps(value)

            await self.client.zadd(key, {value: score})

            if max_items:
                await self.client.zremrangebyrank(key, 0, -(max_items + 1))

            logger.debug(f"{operation_name} successful: {key}")
            return True
        except Exception as exc:  # pragma: no cover - thin wrapper
            logger.error(f"{operation_name} failed for key {key}: {exc}")
            return False

    async def get_from_sorted_set(
        self,
        key: str,
        start: int = 0,
        end: int = -1,
        reverse: bool = True,
        operation_name: str = "Get from sorted set",
    ) -> List[Any]:
        try:
            if reverse:
                items = await self.client.zrevrange(key, start, end)
            else:
                items = await self.client.zrange(key, start, end)

            result = []
            for item in items:
                try:
                    result.append(json.loads(item))
                except (json.JSONDecodeError, TypeError):
                    result.append(item)
            return result
        except Exception as exc:  # pragma: no cover - thin wrapper
            logger.error(f"{operation_name} failed for key {key}: {exc}")
            return []

__all__ = ["RedisDataManager"]

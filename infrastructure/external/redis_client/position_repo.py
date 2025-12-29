"""Position repository mixin."""
from datetime import datetime
from typing import Any, Dict

from infrastructure.config.config import config


class PositionRepoMixin:
    @property
    def _redis_client(self):
        return getattr(self, "client", None)

    async def set_position(self, position_data: Dict[str, Any]) -> bool:
        client = self._redis_client
        if not client:
            return False
        try:
            key = f"bot:{config.TRADING_SYMBOL}:position"
            position_data["updated_at"] = datetime.now().isoformat()
            await client.hset(key, mapping=position_data)
            return True
        except Exception:
            return False

    async def get_position(self) -> Dict[str, str]:
        client = self._redis_client
        if not client:
            return {}
        try:
            key = f"bot:{config.TRADING_SYMBOL}:position"
            return await client.hgetall(key)
        except Exception:
            return {}

    async def update_position_field(self, field: str, value: Any) -> bool:
        client = self._redis_client
        if not client:
            return False
        try:
            key = f"bot:{config.TRADING_SYMBOL}:position"
            await client.hset(key, field, str(value))
            await client.hset(key, "updated_at", datetime.now().isoformat())
            return True
        except Exception:
            return False

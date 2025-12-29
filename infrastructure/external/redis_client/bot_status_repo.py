"""Bot status repository for Redis client."""
import json
from datetime import datetime
from typing import Any, Dict, Optional

from infrastructure.config.config import config


class BotStatusRepoMixin:
    @property
    def _redis_client(self):
        return getattr(self, "client", None)

    async def set_bot_status(self, status: str, metadata: Optional[Dict] = None) -> bool:
        client = self._redis_client
        if not client:
            return False
        try:
            key = f"bot:{config.TRADING_SYMBOL}:status"
            data = {
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {},
            }
            await client.set(key, json.dumps(data))
            return True
        except Exception:
            return False

    async def get_bot_status(self) -> Dict[str, Any]:
        client = self._redis_client
        if not client:
            return {"status": "error", "timestamp": None, "metadata": {}}
        try:
            key = f"bot:{config.TRADING_SYMBOL}:status"
            data = await client.get(key)
            if data:
                return json.loads(data)
            return {"status": "unknown", "timestamp": None, "metadata": {}}
        except Exception as exc:  # pragma: no cover - defensive
            return {"status": "error", "timestamp": None, "metadata": {"error": str(exc)}}

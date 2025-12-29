"""MEXC raw response repository mixin."""
import json
from typing import Any, Dict, Optional


class MexcRawRepoMixin:
    @property
    def _redis_client(self):
        return getattr(self, "client", None)

    async def set_mexc_raw_response(self, endpoint: str, data: Dict[str, Any]) -> bool:
        client = self._redis_client
        if not client:
            return False
        try:
            key = f"mexc:raw_response:{endpoint}"
            payload = {"endpoint": endpoint, "data": data}
            await client.set(key, json.dumps(payload))
            return True
        except Exception:
            return False

    async def get_mexc_raw_response(self, endpoint: str) -> Optional[Dict[str, Any]]:
        client = self._redis_client
        if not client:
            return None
        try:
            key = f"mexc:raw_response:{endpoint}"
            data = await client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception:
            return None

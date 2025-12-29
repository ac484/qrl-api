"""Price repository mixin."""
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from infrastructure.config.config import config


class PriceRepoMixin:
    @property
    def _redis_client(self):
        return getattr(self, "client", None)

    async def set_latest_price(self, price: float, volume: Optional[float] = None, symbol: str = None) -> bool:
        client = self._redis_client
        if not client:
            return False
        try:
            symbol = symbol or config.TRADING_SYMBOL
            key = f"bot:{symbol}:price:latest"
            data = {
                "price": str(price),
                "volume": str(volume) if volume else "0",
                "timestamp": datetime.now().isoformat(),
            }
            await client.set(key, json.dumps(data))
            return True
        except Exception:
            return False

    async def set_cached_price(self, price: float, volume: Optional[float] = None, symbol: str = None) -> bool:
        client = self._redis_client
        if not client:
            return False
        try:
            symbol = symbol or config.TRADING_SYMBOL
            key = f"bot:{symbol}:price:cached"
            data = {
                "price": str(price),
                "volume": str(volume) if volume else "0",
                "timestamp": datetime.now().isoformat(),
            }
            await client.set(key, json.dumps(data), ex=config.CACHE_TTL_PRICE)
            return True
        except Exception:
            return False

    async def get_latest_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        client = self._redis_client
        if not client:
            return None
        try:
            key = f"bot:{symbol}:price:latest"
            data = await client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception:
            return None

    async def get_cached_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        client = self._redis_client
        if not client:
            return None
        try:
            key = f"bot:{symbol}:price:cached"
            data = await client.get(key)
            if data:
                return json.loads(data)
            return await self.get_latest_price(symbol)
        except Exception:
            return None

    async def add_price_to_history(self, price: float, timestamp: Optional[int] = None, symbol: str = None) -> bool:
        client = self._redis_client
        if not client:
            return False
        try:
            symbol = symbol or config.TRADING_SYMBOL
            key = f"bot:{symbol}:price:history"
            timestamp = timestamp or int(datetime.now().timestamp() * 1000)
            await client.zadd(key, {str(price): timestamp})
            await client.zremrangebyrank(key, 0, -1001)
            await client.expire(key, 86400 * 30)
            return True
        except Exception:
            return False

    async def get_price_history(self, limit: int = 100, symbol: str = None) -> List[Dict[str, Any]]:
        client = self._redis_client
        if not client:
            return []
        try:
            symbol = symbol or config.TRADING_SYMBOL
            key = f"bot:{symbol}:price:history"
            prices_with_scores = await client.zrevrange(key, 0, limit - 1, withscores=True)
            return [{"price": float(price), "timestamp": int(ts)} for price, ts in prices_with_scores]
        except Exception:
            return []

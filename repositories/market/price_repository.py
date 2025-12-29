"""Market price persistence helpers."""
from typing import Any, Dict, List, Optional

from infrastructure.external.redis_client.client import redis_client


class PriceRepository:
    """Provides cached market data operations backed by Redis."""

    def __init__(self, client=redis_client):
        self.client = client

    @property
    def connected(self) -> bool:
        return getattr(self.client, "connected", False)

    async def cache_price(self, price: float, volume: Optional[float] = None) -> bool:
        if not self.connected:
            return False
        return await self.client.set_latest_price(price, volume)

    async def get_latest_price(self) -> Dict[str, Any]:
        if not self.connected:
            return {}
        return await self.client.get_latest_price()

    async def add_price_history(self, price: float) -> bool:
        if not self.connected:
            return False
        return await self.client.add_price_to_history(price)

    async def get_price_history(self, limit: int = 100) -> List[float]:
        if not self.connected:
            return []
        return await self.client.get_price_history(limit=limit)

    async def cache_ticker(self, symbol: str, ticker: Dict[str, Any]) -> bool:
        if not self.connected:
            return False
        return await self.client.set_ticker_24hr(symbol, ticker)

    async def get_cached_ticker(self, symbol: str) -> Dict[str, Any]:
        if not self.connected:
            return {}
        return await self.client.get_ticker_24hr(symbol)

    async def cache_price_with_ttl(self, price: float, volume: Optional[float] = None) -> bool:
        if not self.connected:
            return False
        return await self.client.set_cached_price(price, volume)

    async def get_cached_price(self) -> Dict[str, Any]:
        if not self.connected:
            return {}
        return await self.client.get_cached_price()


__all__ = ["PriceRepository"]

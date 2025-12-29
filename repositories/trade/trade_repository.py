"""Trade-related persistence operations."""
from typing import Any, Dict, List, Optional

from infrastructure.external.redis_client.client import redis_client


class TradeRepository:
    """Wraps Redis trade helpers with connection checks."""

    def __init__(self, client=redis_client):
        self.client = client

    @property
    def connected(self) -> bool:
        return getattr(self.client, "connected", False)

    async def increment_daily_trades(self) -> int:
        if not self.connected:
            return 0
        return await self.client.increment_daily_trades()

    async def get_daily_trades(self) -> int:
        if not self.connected:
            return 0
        return await self.client.get_daily_trades()

    async def set_last_trade_time(self, timestamp: Optional[int] = None) -> bool:
        if not self.connected:
            return False
        return await self.client.set_last_trade_time(timestamp)

    async def get_last_trade_time(self) -> Optional[int]:
        if not self.connected:
            return None
        return await self.client.get_last_trade_time()

    async def add_trade_record(self, trade_data: Dict[str, Any]) -> bool:
        if not self.connected:
            return False
        return await self.client.add_trade_record(trade_data)

    async def get_trade_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        if not self.connected:
            return []
        return await self.client.get_trade_history(limit)


__all__ = ["TradeRepository"]

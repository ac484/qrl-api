"""Cost tracking persistence helpers."""
from typing import Any, Dict

from infrastructure.external.redis_client.client import redis_client


class CostRepository:
    """Persist and retrieve cost-related data."""

    def __init__(self, client=redis_client):
        self.client = client

    @property
    def connected(self) -> bool:
        return getattr(self.client, "connected", False)

    async def set_cost_data(self, avg_cost: float, total_invested: float, unrealized_pnl: float) -> bool:
        if not self.connected:
            return False
        return await self.client.set_cost_data(avg_cost, total_invested, unrealized_pnl)

    async def get_cost_data(self) -> Dict[str, Any]:
        if not self.connected:
            return {}
        return await self.client.get_cost_data()


__all__ = ["CostRepository"]

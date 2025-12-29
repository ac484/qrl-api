"""Cost repository mixin."""
from typing import Optional, Dict

from infrastructure.config.config import config


class CostRepoMixin:
    @property
    def _redis_client(self):
        return getattr(self, "client", None)

    async def set_cost_data(self, avg_cost: float, total_invested: float, unrealized_pnl: float = 0, realized_pnl: float = 0) -> bool:
        client = self._redis_client
        if not client:
            return False
        try:
            key = f"bot:{config.TRADING_SYMBOL}:cost"
            cost_data = {
                "avg_cost": str(avg_cost),
                "total_invested": str(total_invested),
                "unrealized_pnl": str(unrealized_pnl),
                "realized_pnl": str(realized_pnl)
            }
            await client.hset(key, mapping=cost_data)
            return True
        except Exception:
            return False
    
    async def get_cost_data(self) -> Optional[Dict[str, str]]:
        client = self._redis_client
        if not client:
            return None
        try:
            key = f"bot:{config.TRADING_SYMBOL}:cost"
            return await client.hgetall(key)
        except Exception:
            return None

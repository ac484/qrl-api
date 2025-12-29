"""Trade history repository mixin."""
import json
from typing import Any, Dict, List

from infrastructure.config.config import config


class TradeHistoryRepoMixin:
    @property
    def _redis_client(self):
        return getattr(self, "client", None)

    async def add_trade_record(self, trade_data: Dict[str, Any]) -> bool:
        client = self._redis_client
        if not client:
            return False
        try:
            key = f"bot:{config.TRADING_SYMBOL}:trades:history"
            await client.zadd(key, {json.dumps(trade_data): trade_data.get("timestamp", 0)})
            await client.zremrangebyrank(key, 0, -501)
            await client.expire(key, 86400 * 30)
            return True
        except Exception:
            return False

    async def get_trade_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        client = self._redis_client
        if not client:
            return []
        try:
            key = f"bot:{config.TRADING_SYMBOL}:trades:history"
            trades_with_scores = await client.zrevrange(key, 0, limit - 1, withscores=True)
            history = []
            for trade_json, timestamp in trades_with_scores:
                try:
                    trade = json.loads(trade_json)
                    trade["timestamp"] = int(timestamp)
                    history.append(trade)
                except Exception:
                    continue
            return history
        except Exception:
            return []

"""Trade counter repository mixin."""
from datetime import datetime, timedelta
from typing import Optional

from infrastructure.config.config import config


class TradeCounterRepoMixin:
    @property
    def _redis_client(self):
        return getattr(self, "client", None)

    async def increment_daily_trades(self) -> int:
        client = self._redis_client
        if not client:
            return 0
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            key = f"bot:{config.TRADING_SYMBOL}:trades:daily:{today}"
            count = await client.incr(key)
            tomorrow = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=2)
            await client.expireat(key, int(tomorrow.timestamp()))
            return count
        except Exception:
            return 0

    async def get_daily_trades(self) -> int:
        client = self._redis_client
        if not client:
            return 0
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            key = f"bot:{config.TRADING_SYMBOL}:trades:daily:{today}"
            count = await client.get(key)
            return int(count) if count else 0
        except Exception:
            return 0

    async def set_last_trade_time(self, timestamp: Optional[int] = None) -> bool:
        client = self._redis_client
        if not client:
            return False
        try:
            key = f"bot:{config.TRADING_SYMBOL}:last_trade_time"
            timestamp = timestamp or int(datetime.now().timestamp())
            await client.set(key, timestamp)
            return True
        except Exception:
            return False

    async def get_last_trade_time(self) -> Optional[int]:
        client = self._redis_client
        if not client:
            return None
        try:
            key = f"bot:{config.TRADING_SYMBOL}:last_trade_time"
            timestamp = await client.get(key)
            return int(timestamp) if timestamp else None
        except Exception:
            return None

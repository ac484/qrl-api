"""
Balance resolver for trading workflow (API + cache fallback).
"""
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class BalanceResolver:
    def __init__(self, mexc_client, redis_client):
        self.mexc = mexc_client
        self.redis = redis_client

    async def get_usdt_balance(self) -> float:
        usdt_balance = 0.0
        try:
            async with self.mexc:
                balance_data: Dict[str, Any] = await self.mexc.get_balance()
            usdt_balance = float(balance_data.get("USDT", {}).get("free", 0))
        except Exception:
            logger.warning("Primary balance fetch failed, attempting cache fallback")

        if usdt_balance <= 0 and hasattr(self.redis, "get_cached_account_balance"):
            cached_balance = await self.redis.get_cached_account_balance()
            if cached_balance:
                usdt_balance = float(
                    cached_balance.get("balances", {}).get("USDT", {}).get("free", 0)
                )
        return usdt_balance

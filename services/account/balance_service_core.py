"""
Balance service for stable QRL/USDT spot balance retrieval with caching.
"""
from datetime import datetime
import logging
from typing import Any, Dict, Optional

from infrastructure.utils.type_safety import safe_float

logger = logging.getLogger(__name__)


class BalanceService:
    """Provide spot balance snapshots with cache fallback."""

    def __init__(self, mexc_client, redis_client, cache_ttl: int = 45):
        self.mexc = mexc_client
        self.redis = redis_client
        self.cache_ttl = cache_ttl

    async def _cache_snapshot(self, snapshot: Dict[str, Any]) -> None:
        if not self.redis:
            return
        try:
            await self.redis.set_cached_account_balance(snapshot, ttl=self.cache_ttl)
            await self.redis.set_mexc_account_balance(snapshot.get("balances", {}))
            qrl = snapshot.get("balances", {}).get("QRL", {})
            price = safe_float(qrl.get("price"))
            if price:
                await self.redis.set_mexc_qrl_price(price)
        except Exception as exc:  # pragma: no cover - best-effort caching
            logger.debug(f"Skipping balance cache write: {exc}")

    async def _cached_response(self, error: Exception) -> Optional[Dict[str, Any]]:
        if not self.redis:
            return None
        cached = await self.redis.get_cached_account_balance()
        if cached:
            cached_response = {
                "success": True,
                "source": "cache",
                "error": str(error),
                **cached,
            }
            return cached_response
        return None

    async def get_account_balance(self, symbol: str = "QRLUSDT") -> Dict[str, Any]:
        try:
            async with self.mexc:
                snapshot = await self.mexc.get_balance_snapshot(symbol)
            await self._cache_snapshot(snapshot)
            snapshot.update(
                {
                    "success": True,
                    "source": "api",
                    "timestamp": datetime.now().isoformat(),
                }
            )
            return snapshot
        except Exception as exc:
            logger.error(f"Failed to fetch live balance: {exc}")
            cached = await self._cached_response(exc)
            if cached:
                return cached
            raise

    @staticmethod
    def to_usd_values(snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Simple helper to enrich balances with USD values."""
        qrl = snapshot.get("balances", {}).get("QRL", {})
        price = safe_float(qrl.get("price"))
        qrl_total = safe_float(qrl.get("total", 0))
        snapshot["balances"]["QRL"].update(
            {"value_usdt": qrl_total * price, "value_usdt_free": safe_float(qrl.get("free")) * price}
        )
        return snapshot

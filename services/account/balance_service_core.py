"""
Balance service for stable QRL/USDT spot balance retrieval with caching.
"""
from datetime import datetime
import logging
from typing import Any, Dict, Optional

from infrastructure.external.mexc_client.account import QRL_USDT_SYMBOL
from infrastructure.utils.type_safety import safe_float

logger = logging.getLogger(__name__)


class BalanceService:
    """Provide spot balance snapshots with cache fallback."""

    def __init__(self, mexc_client, redis_client, cache_ttl: int = 45):
        self.mexc = mexc_client
        self.redis = redis_client
        self.cache_ttl = cache_ttl

    def _has_credentials(self) -> bool:
        if not hasattr(self.mexc, "api_key"):
            return True
        return bool(getattr(self.mexc, "api_key", None) and getattr(self.mexc, "secret_key", None))

    async def _cache_snapshot(self, snapshot: Dict[str, Any]) -> None:
        if not self.redis:
            return
        try:
            await self.redis.set_cached_account_balance(snapshot, ttl=self.cache_ttl)
            await self.redis.set_mexc_account_balance(snapshot.get("balances", {}))
            price = snapshot.get("prices", {}).get(QRL_USDT_SYMBOL)
            if price is not None:
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

    @staticmethod
    def _assert_required_fields(snapshot: Dict[str, Any]) -> None:
        balances = snapshot.setdefault("balances", {})
        balances.setdefault("QRL", {"free": "0", "locked": "0", "total": 0})
        balances.setdefault("USDT", {"free": "0", "locked": "0", "total": 0})
        prices = snapshot.setdefault("prices", {})
        prices.setdefault(QRL_USDT_SYMBOL, 0)

    async def get_account_balance(self) -> Dict[str, Any]:
        if not self._has_credentials():
            cached = await self._cached_response(ValueError("MEXC API credentials required"))
            if cached:
                return cached
            raise ValueError("MEXC API credentials required")

        try:
            async with self.mexc:
                snapshot = await self.mexc.get_balance_snapshot()
            self._assert_required_fields(snapshot)
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
        price_entry = snapshot.get("prices", {}).get(QRL_USDT_SYMBOL)
        raw_price = price_entry if price_entry is not None else qrl.get("price")
        if raw_price is None:
            return snapshot

        price = safe_float(raw_price)
        qrl_total = safe_float(qrl.get("total", 0))
        snapshot["balances"].setdefault("QRL", {})
        snapshot["balances"]["QRL"].setdefault("price", price)
        snapshot["balances"]["QRL"].update(
            {
                "value_usdt": qrl_total * price,
                "value_usdt_free": safe_float(qrl.get("free")) * price,
            }
        )
        return snapshot

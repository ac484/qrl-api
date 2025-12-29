"""
Balance caching helpers separated from Redis client core for clarity.
"""
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class BalanceCacheMixin:
    """Mixin providing balance and valuation caching helpers."""

    @property
    def _redis_client(self):
        return getattr(self, "client", None)

    async def set_mexc_account_balance(self, balance_data: Dict[str, Any]) -> bool:
        client = self._redis_client
        if not client:
            return False
        try:
            key = "mexc:account_balance"
            payload = {
                "balances": balance_data,
                "timestamp": datetime.now().isoformat(),
                "stored_at": int(datetime.now().timestamp() * 1000),
            }
            await client.set(key, json.dumps(payload))
            logger.info("Stored MEXC account balance data")
            return True
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error(f"Failed to store MEXC account balance: {exc}")
            return False

    async def get_mexc_account_balance(self) -> Optional[Dict[str, Any]]:
        client = self._redis_client
        if not client:
            return None
        try:
            key = "mexc:account_balance"
            data = await client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error(f"Failed to get MEXC account balance: {exc}")
            return None

    async def set_mexc_qrl_price(self, price: float, price_data: Optional[Dict[str, Any]] = None) -> bool:
        client = self._redis_client
        if not client:
            return False
        try:
            key = "mexc:qrl_price"
            payload = {
                "price": str(price),
                "price_float": price,
                "timestamp": datetime.now().isoformat(),
                "stored_at": int(datetime.now().timestamp() * 1000),
            }
            if price_data:
                payload["raw_data"] = price_data
            await client.set(key, json.dumps(payload))
            logger.info(f"Stored QRL price: {price} USDT")
            return True
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error(f"Failed to store QRL price: {exc}")
            return False

    async def get_mexc_qrl_price(self) -> Optional[Dict[str, Any]]:
        client = self._redis_client
        if not client:
            return None
        try:
            key = "mexc:qrl_price"
            data = await client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error(f"Failed to get QRL price: {exc}")
            return None

    async def set_mexc_total_value(self, total_value_usdt: float, breakdown: Dict[str, Any]) -> bool:
        client = self._redis_client
        if not client:
            return False
        try:
            key = "mexc:total_value"
            payload = {
                "total_value_usdt": str(total_value_usdt),
                "total_value_float": total_value_usdt,
                "breakdown": breakdown,
                "timestamp": datetime.now().isoformat(),
                "stored_at": int(datetime.now().timestamp() * 1000),
            }
            await client.set(key, json.dumps(payload))
            logger.info(f"Stored total account value: {total_value_usdt} USDT")
            return True
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error(f"Failed to store total value: {exc}")
            return False

    async def get_mexc_total_value(self) -> Optional[Dict[str, Any]]:
        client = self._redis_client
        if not client:
            return None
        try:
            key = "mexc:total_value"
            data = await client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error(f"Failed to get total value: {exc}")
            return None

    async def set_cached_account_balance(self, balance_data: Dict[str, Any], ttl: int = 45) -> bool:
        """Store short-lived balance snapshot for UI stability."""
        client = self._redis_client
        if not client:
            return False
        try:
            key = "mexc:account_balance:cache"
            payload = {
                **balance_data,
                "cached_at": datetime.now().isoformat(),
                "cached_ms": int(datetime.now().timestamp() * 1000),
            }
            await client.setex(key, ttl, json.dumps(payload))
            return True
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error(f"Failed to cache account balance: {exc}")
            return False

    async def get_cached_account_balance(self) -> Optional[Dict[str, Any]]:
        client = self._redis_client
        if not client:
            return None
        try:
            key = "mexc:account_balance:cache"
            data = await client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error(f"Failed to get cached account balance: {exc}")
            return None

__all__ = ["BalanceCacheMixin"]

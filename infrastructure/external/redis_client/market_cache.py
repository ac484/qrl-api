"""
Market cache helpers extracted from Redis client core for clarity.
"""
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from infrastructure.config.config import config

logger = logging.getLogger(__name__)


class MarketCacheMixin:
    """Cache helpers for market data (ticker, order book, trades, klines)."""

    @property
    def _redis_client(self):
        return getattr(self, "client", None)

    async def set_ticker_24hr(self, symbol: str, ticker_data: Dict[str, Any]) -> bool:
        client = self._redis_client
        if not client:
            return False
        try:
            key = f"market:ticker:{symbol}"
            data = {
                "symbol": symbol,
                "data": ticker_data,
                "timestamp": datetime.now().isoformat(),
                "cached_at": int(datetime.now().timestamp() * 1000)
            }
            await client.setex(key, config.CACHE_TTL_TICKER, json.dumps(data))
            logger.debug(f"Cached ticker data for {symbol}")
            return True
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error(f"Failed to cache ticker data for {symbol}: {exc}")
            return False

    async def get_ticker_24hr(self, symbol: str) -> Optional[Dict[str, Any]]:
        client = self._redis_client
        if not client:
            return None
        try:
            key = f"market:ticker:{symbol}"
            data = await client.get(key)
            if data:
                cached = json.loads(data)
                return cached.get("data")
            return None
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error(f"Failed to get ticker data for {symbol}: {exc}")
            return None

    async def set_orderbook(self, symbol: str, orderbook_data: Dict[str, Any]) -> bool:
        client = self._redis_client
        if not client:
            return False
        try:
            key = f"market:orderbook:{symbol}"
            data = {
                "symbol": symbol,
                "data": orderbook_data,
                "timestamp": datetime.now().isoformat(),
                "cached_at": int(datetime.now().timestamp() * 1000)
            }
            await client.setex(key, config.CACHE_TTL_ORDER_BOOK, json.dumps(data))
            logger.debug(f"Cached order book for {symbol}")
            return True
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error(f"Failed to cache order book for {symbol}: {exc}")
            return False

    async def get_orderbook(self, symbol: str) -> Optional[Dict[str, Any]]:
        client = self._redis_client
        if not client:
            return None
        try:
            key = f"market:orderbook:{symbol}"
            data = await client.get(key)
            if data:
                cached = json.loads(data)
                return cached.get("data")
            return None
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error(f"Failed to get order book for {symbol}: {exc}")
            return None

    async def set_recent_trades(self, symbol: str, trades_data: List[Dict[str, Any]]) -> bool:
        client = self._redis_client
        if not client:
            return False
        try:
            key = f"market:trades:{symbol}"
            data = {
                "symbol": symbol,
                "data": trades_data,
                "timestamp": datetime.now().isoformat(),
                "cached_at": int(datetime.now().timestamp() * 1000)
            }
            await client.setex(key, config.CACHE_TTL_TRADES, json.dumps(data))
            logger.debug(f"Cached recent trades for {symbol}")
            return True
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error(f"Failed to cache recent trades for {symbol}: {exc}")
            return False

    async def get_recent_trades(self, symbol: str) -> Optional[List[Dict[str, Any]]]:
        client = self._redis_client
        if not client:
            return None
        try:
            key = f"market:trades:{symbol}"
            data = await client.get(key)
            if data:
                cached = json.loads(data)
                return cached.get("data")
            return None
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error(f"Failed to get recent trades for {symbol}: {exc}")
            return None

    async def set_klines(self, symbol: str, interval: str, klines_data: List[List[Any]], ttl: int) -> bool:
        client = self._redis_client
        if not client:
            return False
        try:
            key = f"market:klines:{symbol}:{interval}"
            data = {
                "symbol": symbol,
                "interval": interval,
                "data": klines_data,
                "timestamp": datetime.now().isoformat(),
                "cached_at": int(datetime.now().timestamp() * 1000)
            }
            await client.setex(key, ttl, json.dumps(data))
            logger.debug(f"Cached klines for {symbol} {interval}")
            return True
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error(f"Failed to cache klines for {symbol}: {exc}")
            return False

    async def get_klines(self, symbol: str, interval: str) -> Optional[List[List[Any]]]:
        client = self._redis_client
        if not client:
            return None
        try:
            key = f"market:klines:{symbol}:{interval}"
            data = await client.get(key)
            if data:
                cached = json.loads(data)
                return cached.get("data")
            return None
        except Exception as exc:  # pragma: no cover - I/O wrapper
            logger.error(f"Failed to get klines for {symbol}: {exc}")
            return None

__all__ = ["MarketCacheMixin"]

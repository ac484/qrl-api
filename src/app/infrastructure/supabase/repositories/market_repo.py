"""
Market data persistence (prices, klines).
"""
import logging
from typing import Dict, List

from . import BaseSupabaseRepository

logger = logging.getLogger(__name__)


class MarketRepository(BaseSupabaseRepository):
    prices_table = "market_prices"
    klines_table = "market_klines"

    def store_price(self, payload: Dict) -> List[Dict]:
        client = self._resolve_client()
        if client is None:
            logger.info("Skipping price store because Supabase is not configured.")
            return []
        return self._execute(client.table(self.prices_table).insert(payload))

    def store_klines(self, payloads: List[Dict]) -> List[Dict]:
        client = self._resolve_client()
        if client is None:
            logger.info("Skipping kline store because Supabase is not configured.")
            return []
        return self._execute(client.table(self.klines_table).insert(payloads))

    def fetch_recent_prices(self, symbol: str, limit: int = 50) -> List[Dict]:
        client = self._resolve_client()
        if client is None:
            logger.info("Skipping price fetch because Supabase is not configured.")
            return []
        query = (
            client.table(self.prices_table)
            .select("*")
            .eq("symbol", symbol)
            .order("timestamp", desc=True)
            .limit(limit)
        )
        return self._execute(query)


__all__ = ["MarketRepository"]

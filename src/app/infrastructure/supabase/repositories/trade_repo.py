"""
Trade persistence helpers.
"""
import logging
from typing import Dict, List, Optional

from . import BaseSupabaseRepository

logger = logging.getLogger(__name__)


class TradeRepository(BaseSupabaseRepository):
    trades_table = "trades"
    executions_table = "executions"

    def record_trade(self, payload: Dict) -> List[Dict]:
        client = self._resolve_client()
        if client is None:
            logger.info("Skipping trade record because Supabase is not configured.")
            return []
        return self._execute(client.table(self.trades_table).insert(payload))

    def record_execution(self, payload: Dict) -> List[Dict]:
        client = self._resolve_client()
        if client is None:
            logger.info("Skipping execution record because Supabase is not configured.")
            return []
        return self._execute(client.table(self.executions_table).insert(payload))

    def list_trades(self, symbol: Optional[str] = None, limit: int = 100) -> List[Dict]:
        client = self._resolve_client()
        if client is None:
            logger.info("Skipping trades list because Supabase is not configured.")
            return []

        query = client.table(self.trades_table).select("*").order("created_at", desc=True)
        if symbol:
            query = query.eq("symbol", symbol)
        if limit:
            query = query.limit(limit)
        return self._execute(query)


__all__ = ["TradeRepository"]

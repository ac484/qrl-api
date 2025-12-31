"""
Order state persistence.
"""
import logging
from typing import Dict, List, Optional

from . import BaseSupabaseRepository

logger = logging.getLogger(__name__)


class OrderRepository(BaseSupabaseRepository):
    orders_table = "orders"

    def record_order(self, payload: Dict) -> List[Dict]:
        client = self._resolve_client()
        if client is None:
            logger.info("Skipping order record because Supabase is not configured.")
            return []
        return self._execute(client.table(self.orders_table).insert(payload))

    def update_status(self, order_id: str, status: str) -> List[Dict]:
        client = self._resolve_client()
        if client is None:
            logger.info("Skipping order status update because Supabase is not configured.")
            return []
        payload = {"status": status}
        return self._execute(
            client.table(self.orders_table).update(payload).eq("order_id", order_id)
        )

    def fetch_order(self, order_id: str) -> List[Dict]:
        client = self._resolve_client()
        if client is None:
            logger.info("Skipping order fetch because Supabase is not configured.")
            return []
        query = client.table(self.orders_table).select("*").eq("order_id", order_id).limit(1)
        return self._execute(query)


__all__ = ["OrderRepository"]

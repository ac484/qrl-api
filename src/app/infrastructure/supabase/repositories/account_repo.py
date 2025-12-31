"""
Account-related Supabase queries (balances, positions, account state).
"""
import logging
from typing import Dict, List, Optional

from . import BaseSupabaseRepository

logger = logging.getLogger(__name__)


class AccountRepository(BaseSupabaseRepository):
    balances_table = "account_balances"
    positions_table = "positions"

    def fetch_balances(self, account_id: str) -> List[Dict]:
        client = self._resolve_client()
        if client is None:
            logger.info("Skipping balance fetch because Supabase is not configured.")
            return []
        query = client.table(self.balances_table).select("*").eq("account_id", account_id)
        return self._execute(query)

    def fetch_positions(self, account_id: str) -> List[Dict]:
        client = self._resolve_client()
        if client is None:
            logger.info("Skipping positions fetch because Supabase is not configured.")
            return []
        query = client.table(self.positions_table).select("*").eq("account_id", account_id)
        return self._execute(query)

    def upsert_balance(self, payload: Dict) -> List[Dict]:
        client = self._resolve_client()
        if client is None:
            logger.info("Skipping balance upsert because Supabase is not configured.")
            return []
        return self._execute(client.table(self.balances_table).upsert(payload))

    def record_position(self, payload: Dict) -> List[Dict]:
        client = self._resolve_client()
        if client is None:
            logger.info("Skipping position record because Supabase is not configured.")
            return []
        return self._execute(client.table(self.positions_table).upsert(payload))


__all__ = ["AccountRepository"]

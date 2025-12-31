"""
Business logic wrapper for account repositories.
"""
from typing import Dict, List

from src.app.infrastructure.supabase.repositories.account_repo import AccountRepository


class AccountService:
    def __init__(self, repo: AccountRepository | None = None) -> None:
        self.repo = repo or AccountRepository()

    def sync_balance(self, account_id: str, balance: Dict) -> List[Dict]:
        payload = {"account_id": account_id, **balance}
        return self.repo.upsert_balance(payload)

    def sync_position(self, account_id: str, position: Dict) -> List[Dict]:
        payload = {"account_id": account_id, **position}
        return self.repo.record_position(payload)

    def get_balances(self, account_id: str) -> List[Dict]:
        return self.repo.fetch_balances(account_id)

    def get_positions(self, account_id: str) -> List[Dict]:
        return self.repo.fetch_positions(account_id)


__all__ = ["AccountService"]

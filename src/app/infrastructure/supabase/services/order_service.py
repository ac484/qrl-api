"""
Order service wrapping Supabase persistence.
"""
from typing import Dict, List

from src.app.infrastructure.supabase.repositories.order_repo import OrderRepository


class OrderService:
    def __init__(self, repo: OrderRepository | None = None) -> None:
        self.repo = repo or OrderRepository()

    def record_order(self, order: Dict) -> List[Dict]:
        return self.repo.record_order(order)

    def update_status(self, order_id: str, status: str) -> List[Dict]:
        return self.repo.update_status(order_id=order_id, status=status)

    def fetch(self, order_id: str) -> List[Dict]:
        return self.repo.fetch_order(order_id)


__all__ = ["OrderService"]

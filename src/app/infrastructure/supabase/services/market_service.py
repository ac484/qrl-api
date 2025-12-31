"""
Market service wrapping Supabase repositories.
"""
from typing import Dict, List

from src.app.infrastructure.supabase.repositories.market_repo import MarketRepository


class MarketService:
    def __init__(self, repo: MarketRepository | None = None) -> None:
        self.repo = repo or MarketRepository()

    def cache_price(self, price_payload: Dict) -> List[Dict]:
        return self.repo.store_price(price_payload)

    def cache_klines(self, klines: List[Dict]) -> List[Dict]:
        return self.repo.store_klines(klines)

    def recent_prices(self, symbol: str, limit: int = 50) -> List[Dict]:
        return self.repo.fetch_recent_prices(symbol=symbol, limit=limit)


__all__ = ["MarketService"]

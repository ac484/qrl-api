"""
Trade-related business wrappers.
"""
from typing import Dict, List, Optional

from src.app.infrastructure.supabase.repositories.trade_repo import TradeRepository


class TradeService:
    def __init__(self, repo: TradeRepository | None = None) -> None:
        self.repo = repo or TradeRepository()

    def record_trade(self, trade: Dict) -> List[Dict]:
        return self.repo.record_trade(trade)

    def record_execution(self, execution: Dict) -> List[Dict]:
        return self.repo.record_execution(execution)

    def recent_trades(self, symbol: Optional[str] = None, limit: int = 100) -> List[Dict]:
        return self.repo.list_trades(symbol=symbol, limit=limit)


__all__ = ["TradeService"]

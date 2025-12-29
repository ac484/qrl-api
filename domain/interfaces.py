"""Domain-level interfaces for repositories and services."""
from typing import Protocol, Any, Dict, List, Optional


class PriceRepositoryProtocol(Protocol):
    async def cache_price(self, price: float, volume: Optional[float] = None) -> bool:
        ...

    async def get_latest_price(self) -> Dict[str, Any]:
        ...

    async def add_price_history(self, price: float) -> bool:
        ...

    async def get_price_history(self, limit: int = 100) -> List[float]:
        ...

    async def cache_ticker(self, symbol: str, ticker: Dict[str, Any]) -> bool:
        ...

    async def get_cached_ticker(self, symbol: str) -> Dict[str, Any]:
        ...


class PositionRepositoryProtocol(Protocol):
    async def set_position(self, position_data: Dict[str, Any]) -> bool:
        ...

    async def get_position(self) -> Dict[str, Any]:
        ...

    async def set_position_layers(self, core_qrl: float, swing_qrl: float, active_qrl: float) -> bool:
        ...

    async def get_position_layers(self) -> Dict[str, Any]:
        ...


class TradeRepositoryProtocol(Protocol):
    async def increment_daily_trades(self) -> int:
        ...

    async def get_daily_trades(self) -> int:
        ...

    async def set_last_trade_time(self, timestamp: Optional[int] = None) -> bool:
        ...

    async def get_last_trade_time(self) -> Optional[int]:
        ...


class CostRepositoryProtocol(Protocol):
    async def set_cost_data(self, avg_cost: float, total_invested: float, unrealized_pnl: float) -> bool:
        ...

    async def get_cost_data(self) -> Dict[str, Any]:
        ...


__all__ = [
    "PriceRepositoryProtocol",
    "PositionRepositoryProtocol",
    "TradeRepositoryProtocol",
    "CostRepositoryProtocol",
]

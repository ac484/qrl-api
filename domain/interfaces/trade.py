"""Trade repository interface"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class ITradeRepository(ABC):
    """Interface for trade history storage"""

    @abstractmethod
    async def add_trade_record(self, trade_data: Dict[str, Any]) -> bool:
        """Add trade to history"""

    @abstractmethod
    async def get_trade_history(self, limit: int) -> List[Dict[str, Any]]:
        """Get trade history"""

    @abstractmethod
    async def get_daily_trades(self) -> int:
        """Get count of trades today"""

    @abstractmethod
    async def increment_daily_trades(self) -> bool:
        """Increment daily trade counter"""

    @abstractmethod
    async def get_last_trade_time(self) -> Optional[int]:
        """Get timestamp of last trade"""

    @abstractmethod
    async def set_last_trade_time(self) -> bool:
        """Update last trade timestamp"""

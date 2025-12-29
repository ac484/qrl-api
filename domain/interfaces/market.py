"""Market data provider interface"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class IMarketDataProvider(ABC):
    """Interface for market data access"""

    @abstractmethod
    async def get_ticker_24hr(self, symbol: str) -> Dict[str, Any]:
        """Get 24-hour ticker data"""

    @abstractmethod
    async def get_klines(self, symbol: str, interval: str, limit: int) -> List[Dict[str, Any]]:
        """Get candlestick data"""

    @abstractmethod
    async def get_ticker_price(self, symbol: str) -> Dict[str, Any]:
        """Get current price"""

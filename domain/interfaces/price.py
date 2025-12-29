"""Price repository interface"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class IPriceRepository(ABC):
    """Interface for price data storage"""

    @abstractmethod
    async def get_latest_price(self) -> Optional[Dict[str, str]]:
        """Get latest price data"""

    @abstractmethod
    async def set_latest_price(self, price: float, volume: float) -> bool:
        """Store latest price"""

    @abstractmethod
    async def get_price_history(self, limit: int) -> List[float]:
        """Get price history"""

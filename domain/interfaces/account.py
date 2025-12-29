"""Account data provider interface"""
from abc import ABC, abstractmethod
from typing import Any, Dict


class IAccountDataProvider(ABC):
    """Interface for account data access"""

    @abstractmethod
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""

    @abstractmethod
    async def create_order(self, symbol: str, side: str, order_type: str, **kwargs) -> Dict[str, Any]:
        """Create a trading order"""

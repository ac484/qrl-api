"""Cost repository interface"""
from abc import ABC, abstractmethod
from typing import Dict


class ICostRepository(ABC):
    """Interface for cost tracking storage"""

    @abstractmethod
    async def get_cost_data(self) -> Dict[str, str]:
        """Get cost tracking data"""

    @abstractmethod
    async def set_cost_data(
        self,
        avg_cost: float,
        total_invested: float,
        unrealized_pnl: float = 0,
        realized_pnl: float = 0,
    ) -> bool:
        """Update cost tracking data"""

"""Position repository interface"""
from abc import ABC, abstractmethod
from typing import Any, Dict


class IPositionRepository(ABC):
    """Interface for position data storage"""

    @abstractmethod
    async def get_position(self) -> Dict[str, str]:
        """Get current position data"""

    @abstractmethod
    async def set_position(self, position_data: Dict[str, Any]) -> bool:
        """Update position data"""

    @abstractmethod
    async def get_position_layers(self) -> Dict[str, str]:
        """Get position layer configuration"""

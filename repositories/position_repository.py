"""
Position Repository - Data access for trading positions
Implements domain interfaces for position management
"""
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PositionRepository:
    """
    Repository for position data storage and retrieval
    Wraps Redis client for position-specific operations
    """
    
    def __init__(self, redis_client):
        """
        Initialize position repository
        
        Args:
            redis_client: Redis client instance
        """
        self.redis = redis_client
    
    async def set_position(self, position_data: Dict[str, Any]) -> bool:
        """
        Store complete position data
        
        Args:
            position_data: Position information including QRL, USDT balances
            
        Returns:
            Success status
        """
        return await self.redis.set_position(position_data)
    
    async def get_position(self) -> Optional[Dict[str, str]]:
        """
        Retrieve current position data
        
        Returns:
            Position data or None if not found
        """
        return await self.redis.get_position()
    
    async def update_position_field(self, field: str, value: Any) -> bool:
        """
        Update a single field in position data
        
        Args:
            field: Field name to update
            value: New value
            
        Returns:
            Success status
        """
        return await self.redis.update_position_field(field, value)
    
    async def set_position_layers(
        self, 
        core_qrl: float, 
        swing_qrl: float, 
        active_qrl: float
    ) -> bool:
        """
        Store position layer allocation
        
        Args:
            core_qrl: Core position quantity (long-term hold)
            swing_qrl: Swing trading quantity
            active_qrl: Active trading quantity
            
        Returns:
            Success status
        """
        return await self.redis.set_position_layers(core_qrl, swing_qrl, active_qrl)
    
    async def get_position_layers(self) -> Optional[Dict[str, str]]:
        """
        Retrieve position layer allocation
        
        Returns:
            Layer data with core, swing, active quantities
        """
        return await self.redis.get_position_layers()
    
    async def get_position_summary(self) -> Dict[str, Any]:
        """
        Get complete position summary
        
        Returns:
            Dict with position, layers, and calculated fields
        """
        position = await self.get_position()
        layers = await self.get_position_layers()
        
        summary = {
            "position": position if position else {},
            "layers": layers if layers else {},
            "has_position": bool(position),
            "has_layers": bool(layers)
        }
        
        # Calculate totals if data exists
        if layers:
            try:
                total_qrl = (
                    float(layers.get("core_qrl", 0)) +
                    float(layers.get("swing_qrl", 0)) +
                    float(layers.get("active_qrl", 0))
                )
                summary["total_qrl"] = total_qrl
            except (ValueError, TypeError):
                logger.warning("Failed to calculate total QRL from layers")
        
        return summary

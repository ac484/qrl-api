"""
Cost Repository - Data access for cost tracking and P&L
Handles average cost, invested amounts, and profit/loss tracking
"""
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class CostRepository:
    """
    Repository for cost and P&L data storage and retrieval
    Wraps Redis client for cost-specific operations
    """
    
    def __init__(self, redis_client):
        """
        Initialize cost repository
        
        Args:
            redis_client: Redis client instance
        """
        self.redis = redis_client
    
    async def set_cost_data(
        self,
        avg_cost: float,
        total_invested: float,
        unrealized_pnl: float = 0,
        realized_pnl: float = 0
    ) -> bool:
        """
        Store cost and P&L data
        
        Args:
            avg_cost: Average cost per unit
            total_invested: Total amount invested (USDT)
            unrealized_pnl: Unrealized profit/loss
            realized_pnl: Realized profit/loss
            
        Returns:
            Success status
        """
        return await self.redis.set_cost_data(
            avg_cost,
            total_invested,
            unrealized_pnl,
            realized_pnl
        )
    
    async def get_cost_data(self) -> Optional[Dict[str, str]]:
        """
        Retrieve cost and P&L data
        
        Returns:
            Dict with avg_cost, total_invested, unrealized_pnl, realized_pnl
        """
        return await self.redis.get_cost_data()
    
    async def calculate_pnl(
        self,
        current_price: float,
        current_quantity: float
    ) -> Dict[str, float]:
        """
        Calculate current P&L based on position
        
        Args:
            current_price: Current market price
            current_quantity: Current holdings quantity
            
        Returns:
            Dict with calculated P&L metrics
        """
        cost_data = await self.get_cost_data()
        
        if not cost_data:
            return {
                "avg_cost": 0,
                "current_value": 0,
                "total_invested": 0,
                "unrealized_pnl": 0,
                "unrealized_pnl_percent": 0,
                "realized_pnl": 0
            }
        
        try:
            avg_cost = float(cost_data.get("avg_cost", 0))
            total_invested = float(cost_data.get("total_invested", 0))
            realized_pnl = float(cost_data.get("realized_pnl", 0))
            
            # Calculate current value
            current_value = current_price * current_quantity
            
            # Calculate unrealized P&L
            cost_basis = avg_cost * current_quantity
            unrealized_pnl = current_value - cost_basis
            
            # Calculate percentage
            unrealized_pnl_percent = 0
            if cost_basis > 0:
                unrealized_pnl_percent = (unrealized_pnl / cost_basis) * 100
            
            return {
                "avg_cost": avg_cost,
                "current_value": current_value,
                "total_invested": total_invested,
                "unrealized_pnl": unrealized_pnl,
                "unrealized_pnl_percent": unrealized_pnl_percent,
                "realized_pnl": realized_pnl,
                "total_pnl": unrealized_pnl + realized_pnl
            }
        
        except (ValueError, TypeError) as e:
            logger.error(f"Failed to calculate P&L: {e}")
            return {
                "avg_cost": 0,
                "current_value": 0,
                "total_invested": 0,
                "unrealized_pnl": 0,
                "unrealized_pnl_percent": 0,
                "realized_pnl": 0,
                "error": str(e)
            }
    
    async def update_after_buy(
        self,
        buy_price: float,
        buy_quantity: float,
        buy_amount_usdt: float
    ) -> bool:
        """
        Update cost data after a buy trade
        
        Args:
            buy_price: Price per unit
            buy_quantity: Quantity purchased
            buy_amount_usdt: Total USDT spent
            
        Returns:
            Success status
        """
        cost_data = await self.get_cost_data()
        
        if not cost_data:
            # First purchase
            return await self.set_cost_data(
                avg_cost=buy_price,
                total_invested=buy_amount_usdt,
                unrealized_pnl=0,
                realized_pnl=0
            )
        
        try:
            old_avg_cost = float(cost_data.get("avg_cost", 0))
            old_total_invested = float(cost_data.get("total_invested", 0))
            realized_pnl = float(cost_data.get("realized_pnl", 0))
            
            # Calculate new average cost
            # This needs current quantity to be accurate
            # For now, just add to total invested
            new_total_invested = old_total_invested + buy_amount_usdt
            
            # Note: This is simplified - proper implementation would need current quantity
            # to calculate new weighted average
            
            return await self.set_cost_data(
                avg_cost=buy_price,  # Simplified
                total_invested=new_total_invested,
                unrealized_pnl=0,  # Will be recalculated
                realized_pnl=realized_pnl
            )
        
        except (ValueError, TypeError) as e:
            logger.error(f"Failed to update cost after buy: {e}")
            return False
    
    async def update_after_sell(
        self,
        sell_price: float,
        sell_quantity: float,
        sell_amount_usdt: float
    ) -> bool:
        """
        Update cost data after a sell trade
        
        Args:
            sell_price: Price per unit
            sell_quantity: Quantity sold
            sell_amount_usdt: Total USDT received
            
        Returns:
            Success status
        """
        cost_data = await self.get_cost_data()
        
        if not cost_data:
            logger.warning("No cost data found for sell update")
            return False
        
        try:
            avg_cost = float(cost_data.get("avg_cost", 0))
            total_invested = float(cost_data.get("total_invested", 0))
            realized_pnl = float(cost_data.get("realized_pnl", 0))
            
            # Calculate realized P&L from this sale
            cost_basis = avg_cost * sell_quantity
            sale_pnl = sell_amount_usdt - cost_basis
            
            # Update realized P&L
            new_realized_pnl = realized_pnl + sale_pnl
            
            # Reduce total invested
            new_total_invested = max(0, total_invested - cost_basis)
            
            return await self.set_cost_data(
                avg_cost=avg_cost,  # Average cost stays the same
                total_invested=new_total_invested,
                unrealized_pnl=0,  # Will be recalculated
                realized_pnl=new_realized_pnl
            )
        
        except (ValueError, TypeError) as e:
            logger.error(f"Failed to update cost after sell: {e}")
            return False

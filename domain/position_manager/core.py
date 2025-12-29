"""
Position management domain logic
"""
from typing import Dict, Any
from infrastructure.config.config import config


class PositionManager:
    """
    Manages position sizing and cost calculations
    """
    
    def __init__(
        self,
        max_position_size: float = None,
        core_position_pct: float = None
    ):
        """
        Initialize position manager
        
        Args:
            max_position_size: Max percentage of balance to use per trade
            core_position_pct: Percentage to keep as core position
        """
        self.max_position_size = max_position_size or config.config.MAX_POSITION_SIZE
        self.core_position_pct = core_position_pct or config.config.CORE_POSITION_PCT
    
    def calculate_buy_quantity(
        self,
        usdt_balance: float,
        price: float
    ) -> Dict[str, float]:
        """
        Calculate quantity to buy
        
        Args:
            usdt_balance: Available USDT
            price: Current price
            
        Returns:
            Dict with 'usdt_to_use' and 'qrl_quantity'
        """
        usdt_to_use = usdt_balance * self.max_position_size
        qrl_quantity = usdt_to_use / price if price > 0 else 0
        
        return {
            "usdt_to_use": usdt_to_use,
            "qrl_quantity": qrl_quantity
        }
    
    def calculate_sell_quantity(
        self,
        total_qrl: float,
        core_qrl: float
    ) -> Dict[str, float]:
        """
        Calculate quantity to sell
        
        Args:
            total_qrl: Total QRL balance
            core_qrl: Core position QRL
            
        Returns:
            Dict with 'tradeable_qrl' and 'qrl_to_sell'
        """
        tradeable_qrl = total_qrl - core_qrl
        qrl_to_sell = tradeable_qrl * self.max_position_size
        
        return {
            "tradeable_qrl": tradeable_qrl,
            "qrl_to_sell": qrl_to_sell
        }
    
    def calculate_new_average_cost(
        self,
        old_avg_cost: float,
        old_total_invested: float,
        qrl_balance: float,
        buy_price: float,
        buy_quantity: float,
        usdt_spent: float
    ) -> Dict[str, float]:
        """
        Calculate new weighted average cost after a buy
        
        Args:
            old_avg_cost: Previous average cost
            old_total_invested: Previous total invested
            qrl_balance: Current QRL balance
            buy_price: Price of new purchase
            buy_quantity: Quantity purchased
            usdt_spent: USDT spent on purchase
            
        Returns:
            Dict with 'new_avg_cost', 'new_total_invested', 'new_qrl_balance'
        """
        new_total_invested = old_total_invested + usdt_spent
        new_qrl_balance = qrl_balance + buy_quantity
        
        if new_qrl_balance > 0:
            new_avg_cost = new_total_invested / new_qrl_balance
        else:
            new_avg_cost = buy_price
        
        return {
            "new_avg_cost": new_avg_cost,
            "new_total_invested": new_total_invested,
            "new_qrl_balance": new_qrl_balance
        }
    
    def calculate_pnl_after_sell(
        self,
        avg_cost: float,
        sell_price: float,
        sell_quantity: float,
        qrl_balance: float,
        old_realized_pnl: float
    ) -> Dict[str, float]:
        """
        Calculate P&L after a sell
        
        Args:
            avg_cost: Average cost basis
            sell_price: Sale price
            sell_quantity: Quantity sold
            qrl_balance: Current QRL balance
            old_realized_pnl: Previous realized P&L
            
        Returns:
            Dict with PnL metrics
        """
        # Realized PnL from this trade
        realized_pnl_from_trade = (sell_price - avg_cost) * sell_quantity
        new_realized_pnl = old_realized_pnl + realized_pnl_from_trade
        
        # Remaining position
        new_qrl_balance = qrl_balance - sell_quantity
        
        # Unrealized PnL on remaining position
        if new_qrl_balance > 0:
            unrealized_pnl = (sell_price - avg_cost) * new_qrl_balance
        else:
            unrealized_pnl = 0
        
        return {
            "realized_pnl_from_trade": realized_pnl_from_trade,
            "new_realized_pnl": new_realized_pnl,
            "new_qrl_balance": new_qrl_balance,
            "unrealized_pnl": unrealized_pnl,
            "avg_cost": avg_cost,  # Stays the same
            "total_invested": avg_cost * new_qrl_balance
        }

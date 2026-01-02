"""Helpers to update position state after trades.

This adapter helps maintain compatibility with existing code that uses
the PositionUpdater pattern while delegating to the Position entity methods.

For new code, prefer calling Position.apply_buy() and Position.apply_sell() directly.
"""
from __future__ import annotations

from decimal import Decimal

from src.app.domain.models.position import Position
from src.app.domain.value_objects import Price, Quantity


class PositionUpdater:
    """Adapter for updating Position entities.
    
    This class maintains compatibility with existing code patterns
    while delegating to Position entity methods.
    
    For new code, use Position methods directly:
    - position.apply_buy(quantity, price)
    - position.apply_sell(quantity, price)
    """

    def apply_buy(self, position: Position, quantity: float, price: float) -> Position:
        """Apply a buy transaction to position.
        
        Args:
            position: Position entity to update
            quantity: Amount being bought
            price: Buy price per unit
        
        Returns:
            The same position (modified in place)
        
        Note:
            Position entity is mutated in place through its apply_buy method.
        """
        qty = Quantity.from_float(quantity)
        prc = Price.from_float(price, position.average_cost.currency if position.average_cost else "USDT")
        
        position.apply_buy(qty, prc)
        return position

    def apply_sell(self, position: Position, quantity: float, price: float) -> Position:
        """Apply a sell transaction to position.
        
        Args:
            position: Position entity to update
            quantity: Amount being sold
            price: Sell price per unit
        
        Returns:
            The same position (modified in place)
        
        Note:
            Position entity is mutated in place through its apply_sell method.
        """
        qty = Quantity.from_float(quantity)
        prc = Price.from_float(price, position.average_cost.currency if position.average_cost else "USDT")
        
        position.apply_sell(qty, prc)
        return position


__all__ = ["PositionUpdater"]

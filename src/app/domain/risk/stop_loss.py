"""Stop-loss policy object for risk management.

Policy Objects encapsulate business rules and decision logic.
They use Value Objects for type-safe domain concepts.
"""
from dataclasses import dataclass

from src.app.domain.value_objects import Price, Percentage


@dataclass(frozen=True, slots=True)
class StopLossGuard:
    """Policy object that determines when to exit a position based on drawdown.
    
    Characteristics:
        - Immutable (frozen=True)
        - Uses Value Objects (Price, Percentage)
        - Encapsulates stop-loss logic
    
    Attributes:
        max_drawdown: Maximum acceptable drawdown percentage (0-1 range)
    
    Example:
        >>> from decimal import Decimal
        >>> guard = StopLossGuard(max_drawdown=Percentage.from_float(0.1))  # 10% max drawdown
        >>> current_price = Price.from_float(90.0, "USDT")
        >>> avg_cost = Price.from_float(100.0, "USDT")
        >>> guard.should_exit(current_price, avg_cost)
        True  # 10% drawdown reached
    """
    max_drawdown: Percentage
    
    def should_exit(self, current_price: Price, avg_cost: Price) -> bool:
        """Determine if position should be exited based on drawdown.
        
        Args:
            current_price: Current market price
            avg_cost: Average cost basis
        
        Returns:
            True if drawdown exceeds max_drawdown threshold
        
        Formula:
            drawdown = (avg_cost - current_price) / avg_cost
            should_exit = drawdown ≥ max_drawdown
        
        Example:
            >>> guard = StopLossGuard(max_drawdown=Percentage.from_float(0.1))
            >>> guard.should_exit(
            ...     current_price=Price.from_float(90.0, "USDT"),
            ...     avg_cost=Price.from_float(100.0, "USDT")
            ... )
            True  # (100-90)/100 = 0.1 = 10% drawdown
        """
        # Validate inputs
        if avg_cost.value <= 0:
            return False
        
        # Ensure same currency
        if current_price.currency != avg_cost.currency:
            raise ValueError(f"Currency mismatch: {current_price.currency} vs {avg_cost.currency}")
        
        # Calculate drawdown
        drawdown_amount = avg_cost.subtract(current_price)
        drawdown_ratio = drawdown_amount.value / avg_cost.value
        
        # Compare to threshold
        return drawdown_ratio >= self.max_drawdown.value


__all__ = ["StopLossGuard"]

"""
Risk validation result types.

These immutable dataclasses replace Dict[str, Any] returns from RiskManager
and validators, providing type safety and clear contracts.
"""

from dataclasses import dataclass

from src.app.domain.value_objects import Quantity


@dataclass(frozen=True, slots=True)
class RiskCheckResult:
    """Result of comprehensive risk check.
    
    Attributes:
        allowed: Whether the trade is allowed to proceed
        reason: Explanation for the decision
        tradeable_quantity: Available quantity to trade (for SELL signals)
        daily_trades: Current daily trade count (if check passed)
    """
    allowed: bool
    reason: str
    tradeable_quantity: Quantity | None = None
    daily_trades: int | None = None


@dataclass(frozen=True, slots=True)
class SellProtectionResult:
    """Result of sell protection validation.
    
    Attributes:
        allowed: Whether sell is allowed
        reason: Explanation for the decision
        tradeable_quantity: Quantity available to sell (if allowed)
    """
    allowed: bool
    reason: str
    tradeable_quantity: Quantity | None = None


@dataclass(frozen=True, slots=True)
class BuyProtectionResult:
    """Result of buy protection validation.
    
    Attributes:
        allowed: Whether buy is allowed
        reason: Explanation for the decision
    """
    allowed: bool
    reason: str


__all__ = [
    "RiskCheckResult",
    "SellProtectionResult",
    "BuyProtectionResult",
]

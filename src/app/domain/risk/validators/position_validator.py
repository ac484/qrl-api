"""
Position Validator

Validates position and balance constraints:
- Core position protection for sells
- USDT balance checks for buys

Uses Value Objects and Position entity for type-safe validation.

Mathematical Formulas:
=====================

Core Position Protection:
    Core_Quantity = Total_Quantity × Core_Position_PCT
    Tradeable_Quantity = Total_Quantity - Core_Quantity
    Allowed = (Tradeable_Quantity > 0) for sell operations

USDT Reserve:
    Available_USDT = USDT_Balance
    Allowed = (Available_USDT > 0) for buy operations
"""

from decimal import Decimal

from src.app.domain.value_objects import Percentage, Quantity
from src.app.domain.models import Position
from src.app.domain.risk.results import SellProtectionResult, BuyProtectionResult


class PositionValidator:
    """
    Validates position and balance constraints

    Purpose:
    -------
    Protects capital by enforcing:
    1. Core position protection (prevents selling core holdings)
    2. USDT balance validation (ensures funds for buying)

    Configuration:
    -------------
    - core_position_pct: Percentage of position protected (Percentage VO)
    """

    def __init__(self, core_position_pct: Percentage):
        """
        Initialize position validator

        Args:
            core_position_pct: Percentage of position to protect (0.0-1.0)
        """
        self.core_position_pct = core_position_pct

    def check_sell_protection(self, position: Position) -> SellProtectionResult:
        """
        Check if sell would violate core position protection

        Formula:
        -------
        Core_Quantity = Total_Quantity × Core_Position_PCT
        Tradeable_Quantity = Total_Quantity - Core_Quantity
        Allowed = (Tradeable_Quantity > 0)

        Purpose:
        -------
        Protects long-term core holdings from being sold.
        Ensures we maintain minimum position for accumulation strategy.

        Example:
        -------
        Total_Quantity = 10,000 QRL
        Core_Position_PCT = 0.70 (70%)

        Calculation:
            Core_Quantity = 10,000 × 0.70 = 7,000 QRL
            Tradeable_Quantity = 10,000 - 7,000 = 3,000 QRL

        Result:
            Allowed: TRUE ✓
            Max_Sell: 3,000 QRL
            Reason: "Tradeable quantity available: 3000.0"

        Args:
            position: Position entity to validate

        Returns:
            SellProtectionResult with allowed status and tradeable quantity

        Note:
            - Core position is NEVER sold
            - Only tradeable portion can be sold
            - Prevents complete position exit
        """
        if not position or not position.has_holdings:
            return SellProtectionResult(
                allowed=False,
                reason="No position to sell",
                tradeable_quantity=None,
            )

        tradeable_quantity = position.get_tradeable_quantity(self.core_position_pct)

        if tradeable_quantity.value <= Decimal("0"):
            return SellProtectionResult(
                allowed=False,
                reason="No tradeable quantity (all in core position)",
                tradeable_quantity=None,
            )

        return SellProtectionResult(
            allowed=True,
            reason=f"Tradeable quantity available: {tradeable_quantity.value}",
            tradeable_quantity=tradeable_quantity,
        )

    def check_buy_protection(self, usdt_balance: Quantity) -> BuyProtectionResult:
        """
        Check if sufficient USDT exists for buying

        Formula:
        -------
        Available_USDT = USDT_Balance
        Allowed = (Available_USDT > 0)

        Note: This simplified version only checks balance > 0.
        Full reserve calculation happens at execution time.

        Purpose:
        -------
        Ensures we maintain USDT balance for:
        1. Emergency liquidity
        2. Future buying opportunities
        3. Fee coverage

        Example:
        -------
        USDT_Balance = Quantity(500, "USDT")

        Simple Check:
            500 > 0 = TRUE ✓

        Args:
            usdt_balance: Current USDT balance (Quantity VO)

        Returns:
            BuyProtectionResult with allowed status

        Note:
            - Simplified check for initial validation
            - Full reserve calculation in execution logic
            - Prevents buying with zero balance
        """
        if usdt_balance.value <= Decimal("0"):
            return BuyProtectionResult(
                allowed=False,
                reason="Insufficient USDT balance"
            )
        return BuyProtectionResult(
            allowed=True,
            reason=f"Sufficient USDT: {usdt_balance.value}"
        )


__all__ = ["PositionValidator"]

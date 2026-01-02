"""
Position Validator

Validates position and balance constraints:
- Core position protection for sells
- USDT balance checks for buys

Mathematical Formulas:
=====================

Core Position Protection:
    Core_QRL = Total_QRL × Core_Position_PCT
    Tradeable_QRL = Total_QRL - Core_QRL
    Allowed = (Tradeable_QRL > 0) for sell operations

USDT Reserve:
    Available_USDT = USDT_Balance
    Allowed = (Available_USDT > 0) for buy operations
"""

from typing import Any, Dict


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
    - core_position_pct: Percentage of position protected (default: 0.70)
    """

    def __init__(self, core_position_pct: float):
        """
        Initialize position validator

        Args:
            core_position_pct: Percentage of position to protect (0.0-1.0)
        """
        self.core_position_pct = core_position_pct

    def check_sell_protection(self, position_layers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if sell would violate core position protection

        Formula:
        -------
        Core_QRL = Total_QRL × Core_Position_PCT
        Tradeable_QRL = Total_QRL - Core_QRL
        Allowed = (Tradeable_QRL > 0)

        Purpose:
        -------
        Protects long-term core holdings from being sold.
        Ensures we maintain minimum position for accumulation strategy.

        Example:
        -------
        Total_QRL = 10,000
        Core_Position_PCT = 0.70 (70%)

        Calculation:
            Core_QRL = 10,000 × 0.70 = 7,000 QRL
            Tradeable_QRL = 10,000 - 7,000 = 3,000 QRL

        Result:
            Allowed: TRUE ✓
            Max_Sell: 3,000 QRL
            Reason: "Tradeable QRL available"

        Args:
            position_layers: Dict containing:
                - total_qrl: Total QRL holdings
                - core_qrl: Protected core position

        Returns:
            Dict with:
                - allowed: bool (True if tradeable QRL exists)
                - tradeable_qrl: float (amount available to sell)
                - reason: str (explanation)

        Note:
            - Core position is NEVER sold
            - Only swing and active layers are tradeable
            - Prevents complete position exit
        """
        if not position_layers:
            return {
                "allowed": False,
                "tradeable_qrl": 0,
                "reason": "No position layers data",
            }

        total_qrl = float(position_layers.get("total_qrl", 0))
        core_qrl = float(position_layers.get("core_qrl", 0))
        tradeable_qrl = total_qrl - core_qrl

        if tradeable_qrl <= 0:
            return {
                "allowed": False,
                "tradeable_qrl": 0,
                "reason": "No tradeable QRL (all in core position)",
            }

        return {
            "allowed": True,
            "tradeable_qrl": tradeable_qrl,
            "reason": "Tradeable QRL available",
        }

    def check_buy_protection(self, usdt_balance: float) -> Dict[str, Any]:
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
        USDT_Balance = 500

        Simple Check:
            500 > 0 = TRUE ✓

        Args:
            usdt_balance: Current USDT balance

        Returns:
            Dict with:
                - allowed: bool (True if balance exists)
                - reason: str (explanation)

        Note:
            - Simplified check for initial validation
            - Full reserve calculation in execution logic
            - Prevents buying with zero balance
        """
        if usdt_balance <= 0:
            return {"allowed": False, "reason": "Insufficient USDT balance"}
        return {"allowed": True, "reason": "Sufficient USDT"}


__all__ = ["PositionValidator"]

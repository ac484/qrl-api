"""
Risk management domain logic (refactored).

Uses modular validators and Value Objects for type-safe risk management.

Mathematical Formulas:
=====================

Daily Trade Limit:
    Allowed = (Daily_Trades_Count < MAX_DAILY_TRADES)

Trade Interval:
    Elapsed_Time = Current_Time - Last_Trade_Time
    Allowed = (Elapsed_Time ≥ MIN_TRADE_INTERVAL)

Core Position Protection:
    Core_Quantity = Total_Quantity × Core_Position_PCT
    Tradeable_Quantity = Total_Quantity - Core_Quantity
    Allowed = (Tradeable_Quantity > 0) for sell operations

USDT Reserve:
    Available_USDT = USDT_Balance
    Allowed = (Available_USDT > 0) for buy operations

Reference: docs/STRATEGY_DESIGN_FORMULAS.md (Section 6: Risk Control)
"""

from src.app.infrastructure.config.env import config
from src.app.domain.value_objects import Percentage, Quantity
from src.app.domain.models import Position
from src.app.domain.risk.results import RiskCheckResult
from src.app.domain.risk.validators.trade_frequency_validator import (
    TradeFrequencyValidator,
)
from src.app.domain.risk.validators.position_validator import PositionValidator


class RiskManager:
    """
    Risk control for trading operations

    Purpose:
    -------
    Orchestrates multiple risk validators to protect capital and enforce
    trading discipline. All checks must pass before trade execution.

    Risk Controls:
    -------------
    1. Daily Trade Limit: Prevents overtrading
    2. Minimum Trade Interval: Prevents rapid-fire trading
    3. Core Position Protection: Preserves long-term holdings
    4. USDT Reserve: Maintains minimum balance

    Configuration:
    -------------
    - MAX_DAILY_TRADES: Default 5 trades per day
    - MIN_TRADE_INTERVAL: Default 300 seconds (5 minutes)
    - CORE_POSITION_PCT: Default 0.70 (70% protected) - Percentage VO
    - USDT_RESERVE_PCT: Default 0.20 (20% reserved)

    For detailed formulas and examples, see:
    - docs/STRATEGY_DESIGN_FORMULAS.md (Section 6)
    - docs/STRATEGY_CALCULATION_EXAMPLES.md (Example 7)
    """

    def __init__(
        self,
        max_daily_trades: int | None = None,
        min_trade_interval: int | None = None,
        core_position_pct: Percentage | None = None,
    ) -> None:
        """
        Initialize risk manager with configurable limits

        Args:
            max_daily_trades: Maximum trades per day (default: 5 from config)
            min_trade_interval: Minimum seconds between trades (default: 300 from config)
            core_position_pct: Core position percentage to protect (Percentage VO, default: 0.70 from config)
        """
        self.max_daily_trades = max_daily_trades or config.MAX_DAILY_TRADES
        self.min_trade_interval = min_trade_interval or config.MIN_TRADE_INTERVAL
        self.core_position_pct = core_position_pct or Percentage.from_float(config.CORE_POSITION_PCT)

        # Initialize validators with Value Objects
        self.frequency_validator = TradeFrequencyValidator(
            max_daily_trades=self.max_daily_trades,
            min_trade_interval=self.min_trade_interval,
        )
        self.position_validator = PositionValidator(
            core_position_pct=self.core_position_pct
        )

    def check_daily_limit(self, daily_trades: int) -> RiskCheckResult:
        """
        Check if daily trade limit has been reached

        Delegates to TradeFrequencyValidator.

        Args:
            daily_trades: Number of trades completed today

        Returns:
            RiskCheckResult with allowed status and reason
        """
        result = self.frequency_validator.check_daily_limit(daily_trades)
        return RiskCheckResult(
            allowed=result["allowed"],
            reason=result["reason"],
        )

    def check_trade_interval(self, last_trade_time: int) -> RiskCheckResult:
        """
        Check if minimum time has elapsed since last trade

        Delegates to TradeFrequencyValidator.

        Args:
            last_trade_time: Unix timestamp of last trade (seconds)

        Returns:
            RiskCheckResult with allowed status and reason
        """
        result = self.frequency_validator.check_trade_interval(last_trade_time)
        return RiskCheckResult(
            allowed=result["allowed"],
            reason=result["reason"],
        )

    def check_sell_protection(self, position: Position) -> RiskCheckResult:
        """
        Check if sell would violate core position protection

        Delegates to PositionValidator.

        Args:
            position: Position entity to validate

        Returns:
            RiskCheckResult with allowed status, tradeable quantity, and reason
        """
        result = self.position_validator.check_sell_protection(position)
        return RiskCheckResult(
            allowed=result.allowed,
            reason=result.reason,
            tradeable_quantity=result.tradeable_quantity,
        )

    def check_buy_protection(self, usdt_balance: Quantity) -> RiskCheckResult:
        """
        Check if sufficient USDT exists for buying

        Delegates to PositionValidator.

        Args:
            usdt_balance: Current USDT balance (Quantity VO)

        Returns:
            RiskCheckResult with allowed status and reason
        """
        result = self.position_validator.check_buy_protection(usdt_balance)
        return RiskCheckResult(
            allowed=result.allowed,
            reason=result.reason,
        )

    def check_all_risks(
        self,
        signal: str,
        daily_trades: int,
        last_trade_time: int,
        position: Position | None,
        usdt_balance: Quantity,
    ) -> RiskCheckResult:
        """
        Execute all risk checks in sequence

        Check Flow:
        ----------
        1. Daily Limit → Stop if reached
        2. Trade Interval → Stop if too soon
        3. For SELL: Position Protection → Stop if no tradeable quantity
        4. For BUY: USDT Check → Stop if insufficient balance

        Formula Summary:
        ---------------
        ALL_CHECKS_PASS =
            (Daily_Trades < MAX) AND
            (Time_Elapsed ≥ MIN_INTERVAL) AND
            (
                (Signal == "SELL" AND Tradeable_Quantity > 0) OR
                (Signal == "BUY" AND USDT_Balance > 0)
            )

        Example - All Checks Pass:
        -------------------------
        Signal: "BUY"
        Daily_Trades: 3 < 5 ✓
        Time_Elapsed: 400s ≥ 300s ✓
        USDT_Balance: Quantity(250, "USDT") > 0 ✓

        Result: RiskCheckResult(
            allowed=True,
            reason="All risk checks passed",
            daily_trades=3
        )

        Example - Daily Limit Hit:
        -------------------------
        Signal: "SELL"
        Daily_Trades: 5 ≥ 5 ❌

        Result: RiskCheckResult(
            allowed=False,
            reason="Daily trade limit reached (5/5)"
        )
        (No further checks executed)

        Args:
            signal: Trading signal ("BUY", "SELL", or "HOLD")
            daily_trades: Number of trades today
            last_trade_time: Timestamp of last trade
            position: Position entity (may be None for first buy)
            usdt_balance: Current USDT balance (Quantity VO)

        Returns:
            RiskCheckResult with:
                - allowed: bool (True if all checks pass)
                - reason: str (explanation)
                - tradeable_quantity: Quantity (only for SELL, if allowed)
                - daily_trades: int (current count, if allowed)

        Note:
            - Checks execute in order, stop at first failure
            - Each check is independent and reusable
            - HOLD signals bypass position-specific checks
            - Failed checks return immediately with reason

        See Also:
            docs/STRATEGY_DESIGN_FORMULAS.md (Section 6: Risk Control)
            docs/STRATEGY_CALCULATION_EXAMPLES.md (Example 7)
        """
        # Check 1: Daily trade limit
        limit_check = self.check_daily_limit(daily_trades)
        if not limit_check.allowed:
            return limit_check

        # Check 2: Trade interval
        interval_check = self.check_trade_interval(last_trade_time)
        if not interval_check.allowed:
            return interval_check

        # Check 3: Signal-specific protections
        if signal == "SELL":
            if not position:
                return RiskCheckResult(
                    allowed=False,
                    reason="No position to sell"
                )
            protection = self.check_sell_protection(position)
            if not protection.allowed:
                return protection
            # Return with tradeable quantity
            return RiskCheckResult(
                allowed=True,
                reason="All risk checks passed",
                tradeable_quantity=protection.tradeable_quantity,
                daily_trades=daily_trades,
            )
        elif signal == "BUY":
            protection = self.check_buy_protection(usdt_balance)
            if not protection.allowed:
                return protection

        # All checks passed
        return RiskCheckResult(
            allowed=True,
            reason="All risk checks passed",
            daily_trades=daily_trades,
        )


__all__ = ["RiskManager"]

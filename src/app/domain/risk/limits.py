"""
Risk management domain logic (migrated).

Preserves existing behavior while relocating under `src/app/domain`.

Mathematical Formulas:
=====================

Daily Trade Limit:
    Allowed = (Daily_Trades_Count < MAX_DAILY_TRADES)

Trade Interval:
    Elapsed_Time = Current_Time - Last_Trade_Time
    Allowed = (Elapsed_Time ≥ MIN_TRADE_INTERVAL)

Core Position Protection:
    Core_QRL = Total_QRL × Core_Position_PCT
    Tradeable_QRL = Total_QRL - Core_QRL
    Allowed = (Tradeable_QRL > 0) for sell operations

USDT Reserve:
    Min_Reserve = Total_Value × USDT_Reserve_PCT
    Available_USDT = USDT_Balance - Min_Reserve
    Allowed = (Available_USDT > 0) for buy operations

Reference: docs/STRATEGY_DESIGN_FORMULAS.md (Section 6: Risk Control)
"""

from typing import Any, Dict
import time

from src.app.infrastructure.config.env import config


class RiskManager:
    """
    Risk control for trading operations
    
    Purpose:
    -------
    Implements multiple layers of risk control to protect capital and enforce
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
    - CORE_POSITION_PCT: Default 0.70 (70% protected)
    - USDT_RESERVE_PCT: Default 0.20 (20% reserved)
    
    For detailed formulas and examples, see:
    - docs/STRATEGY_DESIGN_FORMULAS.md (Section 6)
    - docs/STRATEGY_CALCULATION_EXAMPLES.md (Example 7)
    """

    def __init__(
        self,
        max_daily_trades: int | None = None,
        min_trade_interval: int | None = None,
        core_position_pct: float | None = None,
    ) -> None:
        """
        Initialize risk manager with configurable limits
        
        Args:
            max_daily_trades: Maximum trades per day (default: 5 from config)
            min_trade_interval: Minimum seconds between trades (default: 300 from config)
            core_position_pct: Core position percentage to protect (default: 0.70 from config)
        """
        self.max_daily_trades = max_daily_trades or config.config.MAX_DAILY_TRADES
        self.min_trade_interval = min_trade_interval or config.config.MIN_TRADE_INTERVAL
        self.core_position_pct = core_position_pct or config.config.CORE_POSITION_PCT

    def check_daily_limit(self, daily_trades: int) -> Dict[str, Any]:
        """
        Check if daily trade limit has been reached
        
        Formula:
        -------
        Allowed = (Daily_Trades_Count < MAX_DAILY_TRADES)
        
        Purpose:
        -------
        Prevents overtrading by limiting the number of trades per day.
        Forces discipline and prevents emotional/impulsive trading.
        
        Example:
        -------
        MAX_DAILY_TRADES = 5
        Daily_Trades = 3
        
        Check: 3 < 5 = TRUE ✓
        Remaining: 5 - 3 = 2 trades
        Result: Allowed
        
        Args:
            daily_trades: Number of trades completed today
        
        Returns:
            Dict with:
                - allowed: bool (True if trade can proceed)
                - reason: str (explanation)
        
        Note:
            - Counter resets at 00:00 UTC daily
            - Both BUY and SELL count as separate trades
            - Includes failed trade attempts in some implementations
        """
        if daily_trades >= self.max_daily_trades:
            return {
                "allowed": False,
                "reason": f"Daily trade limit reached ({daily_trades}/{self.max_daily_trades})",
            }
        return {"allowed": True, "reason": "Daily limit OK"}

    def check_trade_interval(self, last_trade_time: int) -> Dict[str, Any]:
        """
        Check if minimum time has elapsed since last trade
        
        Formula:
        -------
        Elapsed_Time = Current_Time - Last_Trade_Time
        Allowed = (Elapsed_Time ≥ MIN_TRADE_INTERVAL)
        
        Purpose:
        -------
        Prevents rapid-fire trading that could:
        1. Incur excessive transaction fees
        2. React to short-term noise
        3. Trigger exchange rate limits
        
        Example:
        -------
        Last_Trade_Time = 10:00:00
        Current_Time = 10:04:10
        MIN_TRADE_INTERVAL = 300 seconds (5 minutes)
        
        Calculation:
            Elapsed = 10:04:10 - 10:00:00 = 250 seconds
            Check: 250 ≥ 300 = FALSE ❌
            Wait: 300 - 250 = 50 seconds
        
        Result: Not allowed, need to wait 50 more seconds
        
        Args:
            last_trade_time: Unix timestamp of last trade (seconds)
                           Use 0 or None for first trade
        
        Returns:
            Dict with:
                - allowed: bool (True if enough time has passed)
                - reason: str (explanation with remaining time if applicable)
        
        Note:
            - Time is in Unix epoch seconds
            - First trade always passes (no previous trade)
            - Consider exchange rate limits when setting interval
        """
        if not last_trade_time:
            return {"allowed": True, "reason": "No previous trade"}

        elapsed = int(time.time()) - last_trade_time
        if elapsed < self.min_trade_interval:
            return {
                "allowed": False,
                "reason": f"Trade interval too short ({elapsed}s < {self.min_trade_interval}s)",
            }
        return {"allowed": True, "reason": "Trade interval OK"}

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
                (calculated values)
        
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
        Min_Reserve = Total_Value × USDT_Reserve_PCT
        Available_USDT = USDT_Balance - Min_Reserve
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
        
        Full Check (at execution):
            Total_Value = 1,000 USDT
            Min_Reserve = 1,000 × 0.20 = 200 USDT
            Available = 500 - 200 = 300 USDT ✓
        
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

    def check_all_risks(
        self,
        signal: str,
        daily_trades: int,
        last_trade_time: int,
        position_layers: Dict[str, Any],
        usdt_balance: float,
    ) -> Dict[str, Any]:
        """
        Execute all risk checks in sequence
        
        Check Flow:
        ----------
        1. Daily Limit → Stop if reached
        2. Trade Interval → Stop if too soon
        3. For SELL: Position Protection → Stop if no tradeable QRL
        4. For BUY: USDT Check → Stop if insufficient balance
        
        Formula Summary:
        ---------------
        ALL_CHECKS_PASS = 
            (Daily_Trades < MAX) AND
            (Time_Elapsed ≥ MIN_INTERVAL) AND
            (
                (Signal == "SELL" AND Tradeable_QRL > 0) OR
                (Signal == "BUY" AND USDT_Balance > 0)
            )
        
        Example - All Checks Pass:
        -------------------------
        Signal: "BUY"
        Daily_Trades: 3 < 5 ✓
        Time_Elapsed: 400s ≥ 300s ✓
        USDT_Balance: 250 > 0 ✓
        
        Result: {
            "allowed": True,
            "reason": "All risk checks passed",
            "daily_trades": 3
        }
        
        Example - Daily Limit Hit:
        -------------------------
        Signal: "SELL"
        Daily_Trades: 5 ≥ 5 ❌
        
        Result: {
            "allowed": False,
            "reason": "Daily trade limit reached (5/5)"
        }
        (No further checks executed)
        
        Args:
            signal: Trading signal ("BUY", "SELL", or "HOLD")
            daily_trades: Number of trades today
            last_trade_time: Timestamp of last trade
            position_layers: Position breakdown data
            usdt_balance: Current USDT balance
        
        Returns:
            Dict with:
                - allowed: bool (True if all checks pass)
                - reason: str (explanation)
                - tradeable_qrl: float (only for SELL, if allowed)
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
        if not limit_check["allowed"]:
            return limit_check

        # Check 2: Trade interval
        interval_check = self.check_trade_interval(last_trade_time)
        if not interval_check["allowed"]:
            return interval_check

        # Check 3: Signal-specific protections
        if signal == "SELL":
            protection = self.check_sell_protection(position_layers)
            if not protection["allowed"]:
                return protection
        elif signal == "BUY":
            protection = self.check_buy_protection(usdt_balance)
            if not protection["allowed"]:
                return protection

        # All checks passed
        return {
            "allowed": True,
            "reason": "All risk checks passed",
            "daily_trades": daily_trades,
        }


__all__ = ["RiskManager"]

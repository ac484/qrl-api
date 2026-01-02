"""
Trade Frequency Validator

Validates trading frequency constraints:
- Daily trade limits
- Minimum trade intervals

Mathematical Formulas:
=====================

Daily Trade Limit:
    Allowed = (Daily_Trades_Count < MAX_DAILY_TRADES)

Trade Interval:
    Elapsed_Time = Current_Time - Last_Trade_Time
    Allowed = (Elapsed_Time ≥ MIN_TRADE_INTERVAL)
"""

from typing import Any, Dict
import time


class TradeFrequencyValidator:
    """
    Validates trade frequency constraints

    Purpose:
    -------
    Prevents overtrading by enforcing:
    1. Maximum daily trade limit
    2. Minimum time between trades

    Configuration:
    -------------
    - max_daily_trades: Maximum trades per day (default: 5)
    - min_trade_interval: Minimum seconds between trades (default: 300)
    """

    def __init__(self, max_daily_trades: int, min_trade_interval: int):
        """
        Initialize trade frequency validator

        Args:
            max_daily_trades: Maximum trades allowed per day
            min_trade_interval: Minimum seconds between consecutive trades
        """
        self.max_daily_trades = max_daily_trades
        self.min_trade_interval = min_trade_interval

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


__all__ = ["TradeFrequencyValidator"]

"""Risk evaluation utilities for trading decisions."""
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from infrastructure.config.config import config


class RiskManager:
    """Evaluate trade risk thresholds based on configuration."""

    def __init__(
        self,
        max_daily_trades: Optional[int] = None,
        min_trade_interval: Optional[int] = None,
    ):
        self.max_daily_trades = max_daily_trades or config.MAX_DAILY_TRADES
        self.min_trade_interval = min_trade_interval or config.MIN_TRADE_INTERVAL

    def evaluate(self, daily_trades: int, last_trade_time: Optional[int]) -> Dict[str, Any]:
        """Return whether a trade is allowed and the reason."""
        if daily_trades >= self.max_daily_trades:
            return {
                "allowed": False,
                "reason": f"Daily trade limit reached ({self.max_daily_trades})",
            }

        if last_trade_time:
            now_ts = int(datetime.now(timezone.utc).timestamp())
            elapsed = now_ts - last_trade_time
            if elapsed < self.min_trade_interval:
                return {
                    "allowed": False,
                    "reason": f"Trade interval too short ({elapsed}s < {self.min_trade_interval}s)",
                }

        return {"allowed": True, "reason": "ok"}


__all__ = ["RiskManager"]

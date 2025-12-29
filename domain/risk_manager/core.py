"""
Risk management domain logic
"""
from typing import Dict, Any
import time
from infrastructure.config.config import config


class RiskManager:
    """
    Risk control for trading operations
    """
    
    def __init__(
        self,
        max_daily_trades: int = None,
        min_trade_interval: int = None,
        core_position_pct: float = None
    ):
        """
        Initialize risk manager
        
        Args:
            max_daily_trades: Maximum trades per day
            min_trade_interval: Minimum seconds between trades
            core_position_pct: Percentage of position to keep as core
        """
        self.max_daily_trades = max_daily_trades or config.config.MAX_DAILY_TRADES
        self.min_trade_interval = min_trade_interval or config.config.MIN_TRADE_INTERVAL
        self.core_position_pct = core_position_pct or config.config.CORE_POSITION_PCT
    
    def check_daily_limit(self, daily_trades: int) -> Dict[str, Any]:
        """
        Check if daily trade limit is exceeded
        
        Args:
            daily_trades: Current number of trades today
            
        Returns:
            Dict with 'allowed' and 'reason'
        """
        if daily_trades >= self.max_daily_trades:
            return {
                "allowed": False,
                "reason": f"Daily trade limit reached ({daily_trades}/{self.max_daily_trades})"
            }
        return {"allowed": True, "reason": "Daily limit OK"}
    
    def check_trade_interval(self, last_trade_time: int) -> Dict[str, Any]:
        """
        Check if minimum trade interval has elapsed
        
        Args:
            last_trade_time: Timestamp of last trade
            
        Returns:
            Dict with 'allowed' and 'reason'
        """
        if not last_trade_time:
            return {"allowed": True, "reason": "No previous trade"}
        
        elapsed = int(time.time()) - last_trade_time
        if elapsed < self.min_trade_interval:
            return {
                "allowed": False,
                "reason": f"Trade interval too short ({elapsed}s < {self.min_trade_interval}s)"
            }
        return {"allowed": True, "reason": "Trade interval OK"}
    
    def check_sell_protection(self, position_layers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if there's tradeable quantity available for selling
        
        Args:
            position_layers: Position layer information
            
        Returns:
            Dict with 'allowed', 'tradeable_qrl', and 'reason'
        """
        if not position_layers:
            return {
                "allowed": False,
                "tradeable_qrl": 0,
                "reason": "No position layers data"
            }
        
        total_qrl = float(position_layers.get("total_qrl", 0))
        core_qrl = float(position_layers.get("core_qrl", 0))
        tradeable_qrl = total_qrl - core_qrl
        
        if tradeable_qrl <= 0:
            return {
                "allowed": False,
                "tradeable_qrl": 0,
                "reason": "No tradeable QRL (all in core position)"
            }
        
        return {
            "allowed": True,
            "tradeable_qrl": tradeable_qrl,
            "reason": "Tradeable QRL available"
        }
    
    def check_buy_protection(self, usdt_balance: float) -> Dict[str, Any]:
        """
        Check if there's sufficient USDT for buying
        
        Args:
            usdt_balance: Available USDT balance
            
        Returns:
            Dict with 'allowed' and 'reason'
        """
        if usdt_balance <= 0:
            return {
                "allowed": False,
                "reason": "Insufficient USDT balance"
            }
        return {"allowed": True, "reason": "Sufficient USDT"}
    
    def check_all_risks(
        self,
        signal: str,
        daily_trades: int,
        last_trade_time: int,
        position_layers: Dict[str, Any],
        usdt_balance: float
    ) -> Dict[str, Any]:
        """
        Run all risk checks for a trading signal
        
        Args:
            signal: Trading signal ("BUY" or "SELL")
            daily_trades: Current daily trade count
            last_trade_time: Last trade timestamp
            position_layers: Position layer data
            usdt_balance: Available USDT
            
        Returns:
            Dict with 'allowed' and 'reason'
        """
        # Check daily limit
        limit_check = self.check_daily_limit(daily_trades)
        if not limit_check["allowed"]:
            return limit_check
        
        # Check trade interval
        interval_check = self.check_trade_interval(last_trade_time)
        if not interval_check["allowed"]:
            return interval_check
        
        # Signal-specific checks
        if signal == "SELL":
            protection = self.check_sell_protection(position_layers)
            if not protection["allowed"]:
                return protection
        
        elif signal == "BUY":
            protection = self.check_buy_protection(usdt_balance)
            if not protection["allowed"]:
                return protection
        
        return {
            "allowed": True,
            "reason": "All risk checks passed",
            "daily_trades": daily_trades
        }

"""
Trade Repository - Data access for trade history and tracking
Handles trade records, daily counters, and timing
"""
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class TradeRepository:
    """
    Repository for trade data storage and retrieval
    Wraps Redis client for trade-specific operations
    """
    
    def __init__(self, redis_client):
        """
        Initialize trade repository
        
        Args:
            redis_client: Redis client instance
        """
        self.redis = redis_client
    
    async def increment_daily_trades(self) -> int:
        """
        Increment daily trade counter
        
        Returns:
            New daily trade count
        """
        return await self.redis.increment_daily_trades()
    
    async def get_daily_trades(self) -> int:
        """
        Get current daily trade count
        
        Returns:
            Number of trades today
        """
        return await self.redis.get_daily_trades()
    
    async def set_last_trade_time(self, timestamp: Optional[int] = None) -> bool:
        """
        Record timestamp of last trade
        
        Args:
            timestamp: Unix timestamp (optional, uses current time if not provided)
            
        Returns:
            Success status
        """
        return await self.redis.set_last_trade_time(timestamp)
    
    async def get_last_trade_time(self) -> Optional[int]:
        """
        Get timestamp of last trade
        
        Returns:
            Unix timestamp or None if no trades
        """
        return await self.redis.get_last_trade_time()
    
    async def add_trade_record(self, trade_data: Dict[str, Any]) -> bool:
        """
        Add trade to history
        
        Args:
            trade_data: Trade information (action, price, quantity, etc.)
            
        Returns:
            Success status
        """
        return await self.redis.add_trade_record(trade_data)
    
    async def get_trade_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieve trade history
        
        Args:
            limit: Maximum number of trades to return
            
        Returns:
            List of trade records
        """
        return await self.redis.get_trade_history(limit)
    
    async def get_trade_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive trade summary
        
        Returns:
            Dict with trade counts, timing, and history
        """
        daily_trades = await self.get_daily_trades()
        last_trade_time = await self.get_last_trade_time()
        recent_trades = await self.get_trade_history(limit=10)
        
        # Calculate time since last trade
        time_since_last_trade = None
        if last_trade_time:
            time_since_last_trade = int(datetime.now().timestamp()) - last_trade_time
        
        # Count buy vs sell trades
        buy_count = sum(1 for t in recent_trades if t.get("action") == "BUY")
        sell_count = sum(1 for t in recent_trades if t.get("action") == "SELL")
        
        return {
            "daily_trades": daily_trades,
            "last_trade_time": last_trade_time,
            "time_since_last_trade_seconds": time_since_last_trade,
            "recent_trades_count": len(recent_trades),
            "recent_buy_count": buy_count,
            "recent_sell_count": sell_count,
            "recent_trades": recent_trades[:5]  # Only return 5 most recent for summary
        }
    
    async def can_trade(
        self, 
        max_daily_trades: int = 10,
        min_interval_seconds: int = 300
    ) -> Dict[str, Any]:
        """
        Check if trading is allowed based on limits
        
        Args:
            max_daily_trades: Maximum trades allowed per day
            min_interval_seconds: Minimum seconds between trades
            
        Returns:
            Dict with allowed status and reasons
        """
        daily_trades = await self.get_daily_trades()
        last_trade_time = await self.get_last_trade_time()
        
        # Check daily limit
        if daily_trades >= max_daily_trades:
            return {
                "allowed": False,
                "reason": f"Daily trade limit reached ({daily_trades}/{max_daily_trades})",
                "daily_trades": daily_trades,
                "time_since_last_trade": None
            }
        
        # Check time interval
        if last_trade_time:
            time_since = int(datetime.now().timestamp()) - last_trade_time
            if time_since < min_interval_seconds:
                return {
                    "allowed": False,
                    "reason": f"Trade interval too short ({time_since}s < {min_interval_seconds}s)",
                    "daily_trades": daily_trades,
                    "time_since_last_trade": time_since
                }
        
        return {
            "allowed": True,
            "reason": "Trading allowed",
            "daily_trades": daily_trades,
            "time_since_last_trade": None if not last_trade_time else int(datetime.now().timestamp()) - last_trade_time
        }

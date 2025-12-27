"""
Redis Client for QRL Trading Bot State Management (Async)
Manages bot status, positions, prices, and trading history
"""
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

import redis.asyncio as redis

from config import config

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis client for trading bot state management (Async)"""
    
    def __init__(self):
        """Initialize Redis connection"""
        self.client: Optional[redis.Redis] = None
        self.connected = False
    
    async def connect(self) -> bool:
        """
        Connect to Redis server
        
        Returns:
            True if connection successful
        """
        try:
            self.client = redis.Redis(
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                password=config.REDIS_PASSWORD,
                db=config.REDIS_DB,
                decode_responses=config.REDIS_DECODE_RESPONSES,
                socket_connect_timeout=config.REDIS_SOCKET_CONNECT_TIMEOUT,
                socket_timeout=config.REDIS_SOCKET_TIMEOUT
            )
            
            # Test connection
            await self.client.ping()
            self.connected = True
            logger.info(f"Connected to Redis at {config.REDIS_HOST}:{config.REDIS_PORT}")
            return True
        
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.connected = False
            return False
    
    async def health_check(self) -> bool:
        """Check Redis connection health"""
        try:
            if self.client:
                await self.client.ping()
                return True
            return False
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False
    
    # ===== Bot Status Management =====
    
    async def set_bot_status(self, status: str, metadata: Optional[Dict] = None) -> bool:
        """
        Set bot status
        
        Args:
            status: Bot status (running, paused, stopped, error)
            metadata: Additional metadata
        """
        try:
            key = f"bot:{config.TRADING_SYMBOL}:status"
            data = {
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            await self.client.set(key, json.dumps(data))
            logger.info(f"Bot status set to: {status}")
            return True
        except Exception as e:
            logger.error(f"Failed to set bot status: {e}")
            return False
    
    async def get_bot_status(self) -> Dict[str, Any]:
        """Get current bot status"""
        try:
            key = f"bot:{config.TRADING_SYMBOL}:status"
            data = await self.client.get(key)
            if data:
                return json.loads(data)
            return {"status": "unknown", "timestamp": None, "metadata": {}}
        except Exception as e:
            logger.error(f"Failed to get bot status: {e}")
            return {"status": "error", "timestamp": None, "metadata": {"error": str(e)}}
    
    # ===== Position Management =====
    
    async def set_position(self, position_data: Dict[str, Any]) -> bool:
        """
        Set current position data
        
        Args:
            position_data: Position information (qrl_balance, usdt_balance, avg_cost, etc.)
        """
        try:
            key = f"bot:{config.TRADING_SYMBOL}:position"
            position_data["updated_at"] = datetime.now().isoformat()
            await self.client.hset(key, mapping=position_data)
            return True
        except Exception as e:
            logger.error(f"Failed to set position: {e}")
            return False
    
    async def get_position(self) -> Dict[str, str]:
        """Get current position data"""
        try:
            key = f"bot:{config.TRADING_SYMBOL}:position"
            return await self.client.hgetall(key)
        except Exception as e:
            logger.error(f"Failed to get position: {e}")
            return {}
    
    async def update_position_field(self, field: str, value: Any) -> bool:
        """Update a specific position field"""
        try:
            key = f"bot:{config.TRADING_SYMBOL}:position"
            await self.client.hset(key, field, str(value))
            await self.client.hset(key, "updated_at", datetime.now().isoformat())
            return True
        except Exception as e:
            logger.error(f"Failed to update position field: {e}")
            return False
    
    # ===== Position Layers Management =====
    
    async def set_position_layers(self, core_qrl: float, swing_qrl: float, active_qrl: float) -> bool:
        """
        Set position layers (core, swing, active)
        
        Args:
            core_qrl: Core position (never trade)
            swing_qrl: Swing position (weekly trading)
            active_qrl: Active position (daily trading)
        """
        try:
            key = f"bot:{config.TRADING_SYMBOL}:position:layers"
            total_qrl = core_qrl + swing_qrl + active_qrl
            core_pct = core_qrl / total_qrl if total_qrl > 0 else 0
            
            layers = {
                "core_qrl": str(core_qrl),
                "swing_qrl": str(swing_qrl),
                "active_qrl": str(active_qrl),
                "total_qrl": str(total_qrl),
                "core_percent": str(core_pct),
                "last_adjust": datetime.now().isoformat()
            }
            await self.client.hset(key, mapping=layers)
            return True
        except Exception as e:
            logger.error(f"Failed to set position layers: {e}")
            return False
    
    async def get_position_layers(self) -> Dict[str, str]:
        """Get position layers"""
        try:
            key = f"bot:{config.TRADING_SYMBOL}:position:layers"
            return await self.client.hgetall(key)
        except Exception as e:
            logger.error(f"Failed to get position layers: {e}")
            return {}
    
    # ===== Price Management =====
    
    async def set_latest_price(self, price: float, volume: Optional[float] = None) -> bool:
        """Set latest price"""
        try:
            key = f"bot:{config.TRADING_SYMBOL}:price:latest"
            data = {
                "price": str(price),
                "volume": str(volume) if volume else "0",
                "timestamp": datetime.now().isoformat()
            }
            await self.client.set(key, json.dumps(data), ex=300)  # 5 minutes TTL
            return True
        except Exception as e:
            logger.error(f"Failed to set latest price: {e}")
            return False
    
    async def get_latest_price(self) -> Optional[Dict[str, Any]]:
        """Get latest price"""
        try:
            key = f"bot:{config.TRADING_SYMBOL}:price:latest"
            data = await self.client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Failed to get latest price: {e}")
            return None
    
    async def add_price_to_history(self, price: float, timestamp: Optional[int] = None) -> bool:
        """
        Add price to historical list
        
        Args:
            price: Price value
            timestamp: Unix timestamp (milliseconds)
        """
        try:
            key = f"bot:{config.TRADING_SYMBOL}:price:history"
            timestamp = timestamp or int(datetime.now().timestamp() * 1000)
            
            # Store as sorted set with timestamp as score
            await self.client.zadd(key, {str(price): timestamp})
            
            # Keep only last 1000 prices
            await self.client.zremrangebyrank(key, 0, -1001)
            
            return True
        except Exception as e:
            logger.error(f"Failed to add price to history: {e}")
            return False
    
    async def get_price_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get price history
        
        Args:
            limit: Number of historical prices to retrieve
        """
        try:
            key = f"bot:{config.TRADING_SYMBOL}:price:history"
            
            # Get last N prices with scores (timestamps)
            prices_with_scores = await self.client.zrevrange(key, 0, limit - 1, withscores=True)
            
            history = []
            for price, timestamp in prices_with_scores:
                history.append({
                    "price": float(price),
                    "timestamp": int(timestamp)
                })
            
            return history
        except Exception as e:
            logger.error(f"Failed to get price history: {e}")
            return []
    
    # ===== Trading Activity Tracking =====
    
    async def increment_daily_trades(self) -> int:
        """Increment daily trade counter"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            key = f"bot:{config.TRADING_SYMBOL}:trades:daily:{today}"
            count = await self.client.incr(key)
            
            # Set expiry to end of day + 1 day
            tomorrow = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=2)
            await self.client.expireat(key, int(tomorrow.timestamp()))
            
            return count
        except Exception as e:
            logger.error(f"Failed to increment daily trades: {e}")
            return 0
    
    async def get_daily_trades(self) -> int:
        """Get today's trade count"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            key = f"bot:{config.TRADING_SYMBOL}:trades:daily:{today}"
            count = await self.client.get(key)
            return int(count) if count else 0
        except Exception as e:
            logger.error(f"Failed to get daily trades: {e}")
            return 0
    
    async def set_last_trade_time(self, timestamp: Optional[int] = None) -> bool:
        """Set timestamp of last trade"""
        try:
            key = f"bot:{config.TRADING_SYMBOL}:last_trade_time"
            timestamp = timestamp or int(datetime.now().timestamp())
            await self.client.set(key, timestamp)
            return True
        except Exception as e:
            logger.error(f"Failed to set last trade time: {e}")
            return False
    
    async def get_last_trade_time(self) -> Optional[int]:
        """Get timestamp of last trade"""
        try:
            key = f"bot:{config.TRADING_SYMBOL}:last_trade_time"
            timestamp = await self.client.get(key)
            return int(timestamp) if timestamp else None
        except Exception as e:
            logger.error(f"Failed to get last trade time: {e}")
            return None
    
    # ===== Trade History =====
    
    async def add_trade_record(self, trade_data: Dict[str, Any]) -> bool:
        """
        Add trade record to history
        
        Args:
            trade_data: Trade information
        """
        try:
            key = f"bot:{config.TRADING_SYMBOL}:trades:history"
            timestamp = int(datetime.now().timestamp() * 1000)
            
            trade_data["timestamp"] = timestamp
            await self.client.zadd(key, {json.dumps(trade_data): timestamp})
            
            # Keep only last 1000 trades
            await self.client.zremrangebyrank(key, 0, -1001)
            
            return True
        except Exception as e:
            logger.error(f"Failed to add trade record: {e}")
            return False
    
    async def get_trade_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get trade history"""
        try:
            key = f"bot:{config.TRADING_SYMBOL}:trades:history"
            trades_raw = await self.client.zrevrange(key, 0, limit - 1)
            
            trades = []
            for trade_str in trades_raw:
                try:
                    trades.append(json.loads(trade_str))
                except json.JSONDecodeError:
                    continue
            
            return trades
        except Exception as e:
            logger.error(f"Failed to get trade history: {e}")
            return []
    
    # ===== Cost Tracking =====
    
    async def set_cost_data(self, avg_cost: float, total_invested: float, unrealized_pnl: float = 0, realized_pnl: float = 0) -> bool:
        """Set cost tracking data"""
        try:
            key = f"bot:{config.TRADING_SYMBOL}:cost"
            cost_data = {
                "avg_cost": str(avg_cost),
                "total_invested": str(total_invested),
                "unrealized_pnl": str(unrealized_pnl),
                "realized_pnl": str(realized_pnl),
                "updated_at": datetime.now().isoformat()
            }
            await self.client.hset(key, mapping=cost_data)
            return True
        except Exception as e:
            logger.error(f"Failed to set cost data: {e}")
            return False
    
    async def get_cost_data(self) -> Dict[str, str]:
        """Get cost tracking data"""
        try:
            key = f"bot:{config.TRADING_SYMBOL}:cost"
            return await self.client.hgetall(key)
        except Exception as e:
            logger.error(f"Failed to get cost data: {e}")
            return {}
    
    async def close(self):
        """Close Redis connection"""
        if self.client:
            await self.client.close()
            self.connected = False
            logger.info("Redis connection closed")


# Singleton instance
redis_client = RedisClient()

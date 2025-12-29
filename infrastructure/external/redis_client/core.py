"""
Redis Client for QRL Trading Bot State Management (Async)
Manages bot status, positions, prices, and trading history
"""
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

import redis.asyncio as redis

from infrastructure.config.config import config
from infrastructure.utils.utils import handle_redis_errors, RedisKeyBuilder
from infrastructure.external.redis_client.balance_cache import BalanceCacheMixin
from infrastructure.external.redis_client.market_cache import MarketCacheMixin

from infrastructure.external.redis_client.bot_status_repo import BotStatusRepoMixin
from infrastructure.external.redis_client.position_repo import PositionRepoMixin
from infrastructure.external.redis_client.position_layers_repo import PositionLayersRepoMixin
from infrastructure.external.redis_client.price_repo import PriceRepoMixin
from infrastructure.external.redis_client.trade_counter_repo import TradeCounterRepoMixin
from infrastructure.external.redis_client.trade_history_repo import TradeHistoryRepoMixin
from infrastructure.external.redis_client.cost_repo import CostRepoMixin
from infrastructure.external.redis_client.mexc_raw_repo import MexcRawRepoMixin

logger = logging.getLogger(__name__)


class RedisClient(
    BalanceCacheMixin,
    MarketCacheMixin,
    BotStatusRepoMixin,
    PositionRepoMixin,
    PositionLayersRepoMixin,
    PriceRepoMixin,
    TradeCounterRepoMixin,
    TradeHistoryRepoMixin,
    CostRepoMixin,
    MexcRawRepoMixin,
):
    """Redis client for trading bot state management (Async)"""
    
    def __init__(self):
        """Initialize Redis connection"""
        self.client: Optional[redis.Redis] = None
        self.pool: Optional[redis.ConnectionPool] = None
        self.connected = False
    
    async def connect(self) -> bool:
        """
        Connect to Redis server with connection pool
        
        Returns:
            True if connection successful
        """
        try:
            # Use REDIS_URL if provided (for Redis Cloud)
            if config.REDIS_URL:
                self.pool = redis.ConnectionPool.from_url(
                    config.REDIS_URL,
                    max_connections=20,
                    decode_responses=config.REDIS_DECODE_RESPONSES,
                    socket_connect_timeout=5,  # Reduced timeout for faster startup
                    socket_timeout=5,  # Reduced timeout
                    health_check_interval=30
                )
                logger.info(f"Created Redis connection pool using REDIS_URL")
            else:
                # Fallback to individual parameters
                self.pool = redis.ConnectionPool(
                    host=config.REDIS_HOST,
                    port=config.REDIS_PORT,
                    password=config.REDIS_PASSWORD,
                    db=config.REDIS_DB,
                    max_connections=20,
                    decode_responses=config.REDIS_DECODE_RESPONSES,
                    socket_connect_timeout=5,  # Reduced timeout for faster startup
                    socket_timeout=5,  # Reduced timeout
                    health_check_interval=30
                )
                logger.info(f"Created Redis connection pool at {config.REDIS_HOST}:{config.REDIS_PORT}")
            
            # Create Redis client from pool
            self.client = redis.Redis(connection_pool=self.pool)
            
            # Test connection with timeout
            await self.client.ping()
            self.connected = True
            logger.info("Redis connection established successfully")
            return True
        
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.connected = False
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to Redis: {e}")
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
    






















# Singleton instance
redis_client = RedisClient()

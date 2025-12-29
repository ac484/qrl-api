"""
Market Service - Market data operations with caching
Coordinates price repositories and MEXC API
"""
import logging
from typing import Dict, Optional, List
from datetime import datetime

from .cache_policy import kline_ttl

logger = logging.getLogger(__name__)


class MarketService:
    """
    Market data operations with caching strategy
    
    Responsibilities:
    - Get ticker data (24h statistics)
    - Get current price
    - Get order book depth
    - Get recent trades
    - Get candlestick (kline) data
    - Manage price caching and history
    """
    
    def __init__(self, mexc_client, redis_client, price_repo):
        self.mexc = mexc_client
        self.redis = redis_client
        self.price_repo = price_repo
    
    async def get_ticker(self, symbol: str) -> Dict:
        """
        Get 24h ticker data with cache-first strategy
        
        Cache TTL: 60 seconds
        """
        try:
            # Try cache first
            cached = await self.redis.get_ticker_24hr(symbol)
            if cached:
                return {
                    "source": "cache",
                    "data": cached,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Fetch from MEXC
            async with self.mexc:
                ticker = await self.mexc.get_ticker_24hr(symbol)
            
            # Cache for 60 seconds
            await self.redis.set_ticker_24hr(symbol, ticker, ttl=60)
            
            return {
                "source": "api",
                "data": ticker,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get ticker for {symbol}: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current price with cache
        
        Returns latest price or fetches from API
        """
        try:
            # Check cached price first
            cached_price = await self.price_repo.get_latest_price(symbol)
            if cached_price:
                return float(cached_price)
            
            # Fetch from API
            async with self.mexc:
                ticker = await self.mexc.get_ticker_24hr(symbol)
                price = float(ticker.get("lastPrice", 0))
            
            # Update cache
            await self.price_repo.set_latest_price(symbol, price)
            
            return price
            
        except Exception as e:
            logger.error(f"Failed to get current price for {symbol}: {str(e)}")
            return None
    
    async def get_orderbook(self, symbol: str, limit: int = 100) -> Dict:
        """
        Get order book depth
        
        Cache TTL: 10 seconds
        """
        try:
            # Try cache first
            cached = await self.redis.get_orderbook(symbol)
            if cached:
                return {
                    "source": "cache",
                    "data": cached,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Fetch from MEXC
            async with self.mexc:
                orderbook = await self.mexc.get_orderbook(symbol, limit=limit)
            
            # Cache for 10 seconds
            await self.redis.set_orderbook(symbol, orderbook, ttl=10)
            
            return {
                "source": "api",
                "data": orderbook,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get orderbook for {symbol}: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_recent_trades(self, symbol: str, limit: int = 500) -> Dict:
        """
        Get recent trades
        
        Cache TTL: 30 seconds
        """
        try:
            # Try cache first
            cached = await self.redis.get_recent_trades(symbol)
            if cached:
                return {
                    "source": "cache",
                    "data": cached,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Fetch from MEXC
            async with self.mexc:
                trades = await self.mexc.get_recent_trades(symbol, limit=limit)
            
            # Cache for 30 seconds
            await self.redis.set_recent_trades(symbol, trades, ttl=30)
            
            return {
                "source": "api",
                "data": trades,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get recent trades for {symbol}: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_klines(
        self,
        symbol: str,
        interval: str = "1m",
        limit: int = 100
    ) -> Dict:
        """
        Get candlestick (kline) data
        
        Cache TTL: varies by interval
        - 1m: 60 seconds
        - 5m: 300 seconds
        - 1h: 3600 seconds
        """
        try:
            # Determine cache TTL based on interval
            ttl = kline_ttl(interval)
            
            # Try cache first
            cached = await self.redis.get_klines(symbol, interval)
            if cached:
                return {
                    "source": "cache",
                    "data": cached,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Fetch from MEXC
            async with self.mexc:
                klines = await self.mexc.get_klines(symbol, interval=interval, limit=limit)
            
            # Cache with appropriate TTL
            await self.redis.set_klines(symbol, interval, klines, ttl=ttl)
            
            return {
                "source": "api",
                "data": klines,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get klines for {symbol}: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def update_price_cache(self, symbol: str) -> Dict:
        """
        Update price cache and history
        
        Called periodically to maintain price history for MA calculations
        """
        try:
            # Get current price
            price = await self.get_current_price(symbol)
            if not price:
                return {
                    "success": False,
                    "error": "Failed to get current price",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Add to price history
            await self.price_repo.add_price_to_history(symbol, price)
            
            # Update latest price cache
            await self.price_repo.set_cached_price(symbol, price)
            
            return {
                "success": True,
                "symbol": symbol,
                "price": price,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to update price cache for {symbol}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_price_statistics(self, symbol: str, limit: int = 100) -> Dict:
        """
        Get price statistics from history
        
        Returns min, max, average, latest from price history
        """
        try:
            stats = await self.price_repo.get_price_statistics(symbol, limit=limit)
            return {
                "success": True,
                "symbol": symbol,
                "stats": stats,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get price statistics for {symbol}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

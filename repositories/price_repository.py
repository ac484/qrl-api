"""
Price Repository - Data access for price data
Handles price caching and history
"""
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class PriceRepository:
    """
    Repository for price data storage and retrieval
    Wraps Redis client for price-specific operations
    """
    
    def __init__(self, redis_client):
        """
        Initialize price repository
        
        Args:
            redis_client: Redis client instance
        """
        self.redis = redis_client
    
    async def set_latest_price(
        self, 
        price: float, 
        volume: Optional[float] = None
    ) -> bool:
        """
        Store latest price data
        
        Args:
            price: Current price
            volume: Trading volume (optional)
            
        Returns:
            Success status
        """
        return await self.redis.set_latest_price(price, volume)
    
    async def get_latest_price(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve latest price data
        
        Returns:
            Price data with timestamp
        """
        return await self.redis.get_latest_price()
    
    async def set_cached_price(
        self, 
        price: float, 
        volume: Optional[float] = None
    ) -> bool:
        """
        Store cached price for quick access
        
        Args:
            price: Current price
            volume: Trading volume (optional)
            
        Returns:
            Success status
        """
        return await self.redis.set_cached_price(price, volume)
    
    async def get_cached_price(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached price data
        
        Returns:
            Cached price data
        """
        return await self.redis.get_cached_price()
    
    async def add_price_to_history(
        self, 
        price: float, 
        timestamp: Optional[int] = None
    ) -> bool:
        """
        Add price to historical data
        
        Args:
            price: Price value
            timestamp: Unix timestamp (optional, uses current time if not provided)
            
        Returns:
            Success status
        """
        return await self.redis.add_price_to_history(price, timestamp)
    
    async def get_price_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve price history
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of price records with timestamps
        """
        return await self.redis.get_price_history(limit)
    
    async def get_price_statistics(self, limit: int = 100) -> Dict[str, Any]:
        """
        Calculate price statistics from history
        
        Args:
            limit: Number of historical records to analyze
            
        Returns:
            Dict with min, max, average, and latest price
        """
        history = await self.get_price_history(limit)
        
        if not history:
            return {
                "count": 0,
                "min": None,
                "max": None,
                "average": None,
                "latest": None
            }
        
        prices = [float(record.get("price", 0)) for record in history if "price" in record]
        
        if not prices:
            return {
                "count": 0,
                "min": None,
                "max": None,
                "average": None,
                "latest": None
            }
        
        return {
            "count": len(prices),
            "min": min(prices),
            "max": max(prices),
            "average": sum(prices) / len(prices),
            "latest": prices[0] if prices else None
        }

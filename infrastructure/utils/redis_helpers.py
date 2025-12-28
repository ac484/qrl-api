"""
Redis helper functions to reduce code duplication
Consolidated common patterns from redis_client.py
"""
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class RedisDataManager:
    """
    Generic Redis data manager that handles common patterns:
    - JSON serialization/deserialization
    - Error handling
    - Logging
    - Metadata attachment
    """
    
    def __init__(self, redis_client):
        self.client = redis_client
    
    async def set_json_data(
        self,
        key: str,
        data: Dict[str, Any],
        ttl: Optional[int] = None,
        add_timestamp: bool = True,
        operation_name: str = "Set data"
    ) -> bool:
        """
        Generic method to set JSON data in Redis
        
        Args:
            key: Redis key
            data: Data to store (will be JSON serialized)
            ttl: Optional TTL in seconds
            add_timestamp: Whether to add timestamp to data
            operation_name: Name for logging
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add timestamp if requested
            if add_timestamp:
                data["timestamp"] = datetime.now().isoformat()
                data["stored_at"] = int(datetime.now().timestamp() * 1000)
            
            # Serialize and store
            json_data = json.dumps(data)
            
            if ttl:
                await self.client.setex(key, ttl, json_data)
            else:
                await self.client.set(key, json_data)
            
            logger.debug(f"{operation_name} successful: {key}")
            return True
            
        except Exception as e:
            logger.error(f"{operation_name} failed for key {key}: {e}")
            return False
    
    async def get_json_data(
        self,
        key: str,
        default: Any = None,
        operation_name: str = "Get data"
    ) -> Optional[Dict[str, Any]]:
        """
        Generic method to get JSON data from Redis
        
        Args:
            key: Redis key
            default: Default value if key doesn't exist or parsing fails
            operation_name: Name for logging
            
        Returns:
            Deserialized data or default value
        """
        try:
            data = await self.client.get(key)
            if data:
                return json.loads(data)
            return default
        except Exception as e:
            logger.error(f"{operation_name} failed for key {key}: {e}")
            return default
    
    async def set_hash_data(
        self,
        key: str,
        data: Dict[str, Any],
        operation_name: str = "Set hash"
    ) -> bool:
        """
        Generic method to set hash data in Redis
        
        Args:
            key: Redis key
            data: Data to store as hash
            operation_name: Name for logging
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert all values to strings for Redis hash
            string_data = {k: str(v) for k, v in data.items()}
            await self.client.hset(key, mapping=string_data)
            logger.debug(f"{operation_name} successful: {key}")
            return True
        except Exception as e:
            logger.error(f"{operation_name} failed for key {key}: {e}")
            return False
    
    async def get_hash_data(
        self,
        key: str,
        operation_name: str = "Get hash"
    ) -> Dict[str, str]:
        """
        Generic method to get hash data from Redis
        
        Args:
            key: Redis key
            operation_name: Name for logging
            
        Returns:
            Hash data or empty dict
        """
        try:
            return await self.client.hgetall(key)
        except Exception as e:
            logger.error(f"{operation_name} failed for key {key}: {e}")
            return {}
    
    async def add_to_sorted_set(
        self,
        key: str,
        value: Any,
        score: float,
        max_items: Optional[int] = None,
        operation_name: str = "Add to sorted set"
    ) -> bool:
        """
        Add item to sorted set with optional size limit
        
        Args:
            key: Redis key
            value: Value to add (will be JSON serialized if dict)
            score: Score for sorting
            max_items: Maximum items to keep (removes oldest)
            operation_name: Name for logging
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Serialize value if it's a dict
            if isinstance(value, dict):
                value = json.dumps(value)
            
            # Add to sorted set
            await self.client.zadd(key, {value: score})
            
            # Trim if max_items specified
            if max_items:
                await self.client.zremrangebyrank(key, 0, -(max_items + 1))
            
            logger.debug(f"{operation_name} successful: {key}")
            return True
            
        except Exception as e:
            logger.error(f"{operation_name} failed for key {key}: {e}")
            return False
    
    async def get_from_sorted_set(
        self,
        key: str,
        start: int = 0,
        end: int = -1,
        reverse: bool = True,
        operation_name: str = "Get from sorted set"
    ) -> List[Any]:
        """
        Get items from sorted set
        
        Args:
            key: Redis key
            start: Start index
            end: End index
            reverse: Whether to get in reverse order (highest score first)
            operation_name: Name for logging
            
        Returns:
            List of items (deserialized if JSON)
        """
        try:
            if reverse:
                items = await self.client.zrevrange(key, start, end)
            else:
                items = await self.client.zrange(key, start, end)
            
            # Try to deserialize JSON items
            result = []
            for item in items:
                try:
                    result.append(json.loads(item))
                except (json.JSONDecodeError, TypeError):
                    result.append(item)
            
            return result
            
        except Exception as e:
            logger.error(f"{operation_name} failed for key {key}: {e}")
            return []


def create_metadata(additional_data: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Create standard metadata object
    
    Args:
        additional_data: Additional fields to include
        
    Returns:
        Metadata dict with timestamp and optional additional data
    """
    metadata = {
        "timestamp": datetime.now().isoformat(),
        "stored_at": int(datetime.now().timestamp() * 1000)
    }
    
    if additional_data:
        metadata.update(additional_data)
    
    return metadata
